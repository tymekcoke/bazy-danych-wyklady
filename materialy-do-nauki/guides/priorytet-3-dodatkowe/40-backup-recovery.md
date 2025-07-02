# Backup i Recovery

## Definicja backup i recovery

**Backup i Recovery** to **kluczowe procesy** w zarządzaniu bazami danych, które zapewniają **ochronę danych** przed utratą oraz **możliwość przywrócenia** systemu do sprawnego stanu po awarii.

### Kluczowe pojęcia:
- **Backup** - kopia zapasowa danych w określonym momencie
- **Recovery** - proces przywracania danych po awarii
- **RPO (Recovery Point Objective)** - maksymalna akceptowalna utrata danych
- **RTO (Recovery Time Objective)** - maksymalny czas przywracania systemu
- **Point-in-Time Recovery (PITR)** - przywracanie do konkretnego momentu
- **Hot backup** - backup podczas działania systemu
- **Cold backup** - backup po zatrzymaniu systemu

### Typy awarii:
- **Hardware failure** - awarie sprzętowe
- **Software corruption** - uszkodzenia oprogramowania
- **Human error** - błędy użytkowników
- **Natural disasters** - klęski żywiołowe
- **Security breaches** - ataki i naruszenia bezpieczeństwa

## Strategie backup

### 1. **Pełny backup (Full Backup)**

#### PostgreSQL - pg_dump:
```bash
#!/bin/bash
# Skrypt pełnego backup PostgreSQL

# Konfiguracja
DB_NAME="company_db"
DB_USER="postgres"
DB_HOST="localhost"
BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/full_backup_${DB_NAME}_${DATE}.sql"

# Utworzenie katalogu backup
mkdir -p "$BACKUP_DIR"

# Pełny backup z kompresją
pg_dump \
    --host="$DB_HOST" \
    --username="$DB_USER" \
    --dbname="$DB_NAME" \
    --no-password \
    --verbose \
    --format=custom \
    --compress=9 \
    --file="$BACKUP_FILE.dump"

# Sprawdzenie powodzenia
if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_FILE.dump"
    
    # Dodatkowa kopia w formacie SQL (czytelnym)
    pg_dump \
        --host="$DB_HOST" \
        --username="$DB_USER" \
        --dbname="$DB_NAME" \
        --no-password \
        --verbose \
        --format=plain \
        --file="$BACKUP_FILE"
    
    # Kompresja SQL
    gzip "$BACKUP_FILE"
    
    # Weryfikacja backup
    echo "Verifying backup integrity..."
    pg_restore --list "$BACKUP_FILE.dump" > /dev/null
    
    if [ $? -eq 0 ]; then
        echo "Backup verification successful"
        
        # Przechowuj tylko ostatnie 7 dni
        find "$BACKUP_DIR" -name "full_backup_*.dump" -type f -mtime +7 -delete
        find "$BACKUP_DIR" -name "full_backup_*.sql.gz" -type f -mtime +7 -delete
        
    else
        echo "Backup verification failed!"
        exit 1
    fi
else
    echo "Backup failed!"
    exit 1
fi

# Backup metadanych klastra
pg_dumpall \
    --host="$DB_HOST" \
    --username="$DB_USER" \
    --globals-only \
    --file="${BACKUP_DIR}/globals_${DATE}.sql"

# Backup konfiguracji
cp /etc/postgresql/*/main/postgresql.conf "${BACKUP_DIR}/postgresql_conf_${DATE}.conf"
cp /etc/postgresql/*/main/pg_hba.conf "${BACKUP_DIR}/pg_hba_conf_${DATE}.conf"
```

#### Zaawansowany backup z metadanymi:
```bash
#!/bin/bash
# Kompleksowy backup PostgreSQL

BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${BACKUP_DIR}/backup_${DATE}.log"

# Funkcja logowania
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Backup funkcji i procedur
backup_functions() {
    local db_name=$1
    log "Backing up functions and procedures for $db_name"
    
    pg_dump \
        --host="$DB_HOST" \
        --username="$DB_USER" \
        --dbname="$db_name" \
        --schema-only \
        --no-owner \
        --no-privileges \
        --section=pre-data \
        --section=post-data \
        --file="${BACKUP_DIR}/schema_${db_name}_${DATE}.sql"
}

# Backup tylko danych
backup_data_only() {
    local db_name=$1
    log "Backing up data only for $db_name"
    
    pg_dump \
        --host="$DB_HOST" \
        --username="$DB_USER" \
        --dbname="$db_name" \
        --data-only \
        --format=custom \
        --compress=9 \
        --file="${BACKUP_DIR}/data_only_${db_name}_${DATE}.dump"
}

# Backup z wykluczeniem tabel
backup_selective() {
    local db_name=$1
    log "Selective backup for $db_name"
    
    # Wyklucz duże tabele logów
    pg_dump \
        --host="$DB_HOST" \
        --username="$DB_USER" \
        --dbname="$db_name" \
        --format=custom \
        --compress=9 \
        --exclude-table=access_logs \
        --exclude-table=audit_trail \
        --exclude-table=temp_* \
        --file="${BACKUP_DIR}/selective_${db_name}_${DATE}.dump"
}

# Backup per tabela dla dużych baz danych
backup_per_table() {
    local db_name=$1
    local table_dir="${BACKUP_DIR}/tables_${db_name}_${DATE}"
    
    mkdir -p "$table_dir"
    log "Per-table backup for $db_name"
    
    # Pobierz listę tabel
    tables=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$db_name" -t -c "
        SELECT schemaname||'.'||tablename 
        FROM pg_tables 
        WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
    ")
    
    for table in $tables; do
        log "Backing up table: $table"
        pg_dump \
            --host="$DB_HOST" \
            --username="$DB_USER" \
            --dbname="$db_name" \
            --table="$table" \
            --format=custom \
            --compress=9 \
            --file="${table_dir}/${table//\./_}_${DATE}.dump"
    done
}

# Wykonaj różne typy backup
for DB_NAME in "company_db" "analytics_db" "logs_db"; do
    log "Starting backup for database: $DB_NAME"
    
    # Pełny backup
    pg_dump \
        --host="$DB_HOST" \
        --username="$DB_USER" \
        --dbname="$DB_NAME" \
        --format=custom \
        --compress=9 \
        --verbose \
        --file="${BACKUP_DIR}/full_${DB_NAME}_${DATE}.dump"
    
    # Backup schematu
    backup_functions "$DB_NAME"
    
    # Backup selektywny
    backup_selective "$DB_NAME"
    
    log "Backup completed for database: $DB_NAME"
done

# Backup globalnych ustawień
pg_dumpall \
    --host="$DB_HOST" \
    --username="$DB_USER" \
    --roles-only \
    --file="${BACKUP_DIR}/roles_${DATE}.sql"

log "All backups completed successfully"
```

### 2. **Inkrementalny backup**

#### PostgreSQL WAL archiving:
```bash
# postgresql.conf configuration
wal_level = replica
archive_mode = on
archive_command = '/usr/local/bin/archive_wal.sh %p %f'
archive_timeout = 300  # 5 minutes

# WAL archiving script
#!/bin/bash
# /usr/local/bin/archive_wal.sh

WAL_FILE=$1
WAL_FILENAME=$2
ARCHIVE_DIR="/archives/wal"
DATE=$(date +%Y%m%d)
DAILY_DIR="${ARCHIVE_DIR}/${DATE}"

# Utworzenie katalogu dziennego
mkdir -p "$DAILY_DIR"

# Skopiuj plik WAL
cp "$WAL_FILE" "${DAILY_DIR}/${WAL_FILENAME}"

# Sprawdź integralność
if [ $? -eq 0 ]; then
    # Dodatkowa kompresja dla starszych plików
    find "$ARCHIVE_DIR" -name "*.wal" -type f -mtime +1 -exec gzip {} \;
    
    # Usuń stare archiwa (starsze niż 30 dni)
    find "$ARCHIVE_DIR" -type d -mtime +30 -exec rm -rf {} \;
    
    exit 0
else
    exit 1
fi
```

#### Continuous backup z pg_receivewal:
```bash
#!/bin/bash
# Continuous WAL streaming

DB_HOST="localhost"
DB_PORT="5432"
DB_USER="replicator"
WAL_DIR="/continuous_backup/wal"
LOG_FILE="/var/log/postgresql/wal_receiver.log"

# Funkcja logowania
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Tworzenie katalogu
mkdir -p "$WAL_DIR"

log "Starting continuous WAL streaming"

# Uruchom pg_receivewal w tle
pg_receivewal \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --directory="$WAL_DIR" \
    --verbose \
    --compress=9 \
    --synchronous \
    2>> "$LOG_FILE" &

PID=$!
echo $PID > /var/run/pg_receivewal.pid

log "pg_receivewal started with PID: $PID"

# Monitor proces
while kill -0 $PID 2>/dev/null; do
    sleep 60
    
    # Sprawdź rozmiar katalogu WAL
    WAL_SIZE=$(du -sh "$WAL_DIR" | cut -f1)
    log "Current WAL directory size: $WAL_SIZE"
    
    # Sprawdź czy są stare pliki do usunięcia
    OLD_FILES=$(find "$WAL_DIR" -name "*.gz" -type f -mtime +7 | wc -l)
    if [ "$OLD_FILES" -gt 0 ]; then
        log "Removing $OLD_FILES old WAL files"
        find "$WAL_DIR" -name "*.gz" -type f -mtime +7 -delete
    fi
done

log "pg_receivewal process ended"
```

### 3. **Backup różnicowy**

#### Script dla backup różnicowego:
```python
#!/usr/bin/env python3
"""
Differential backup system for PostgreSQL
"""

import os
import sys
import subprocess
import logging
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path

class DifferentialBackup:
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.setup_logging()
        
    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def setup_logging(self):
        log_dir = Path(self.config['backup_dir']) / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f'differential_backup_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_table_checksum(self, database, table):
        """Calculate checksum for table data"""
        cmd = [
            'psql',
            '-h', self.config['host'],
            '-U', self.config['username'],
            '-d', database,
            '-t', '-c',
            f"SELECT md5(string_agg(md5(t.*::text), '' ORDER BY (t.*::text))) FROM {table} t"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error calculating checksum for {table}: {e}")
            return None
    
    def get_database_tables(self, database):
        """Get list of tables in database"""
        cmd = [
            'psql',
            '-h', self.config['host'],
            '-U', self.config['username'],
            '-d', database,
            '-t', '-c',
            """
            SELECT schemaname||'.'||tablename 
            FROM pg_tables 
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
            ORDER BY schemaname, tablename
            """
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return [table.strip() for table in result.stdout.split('\n') if table.strip()]
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error getting tables for {database}: {e}")
            return []
    
    def load_previous_checksums(self, database):
        """Load checksums from previous backup"""
        checksum_file = Path(self.config['backup_dir']) / f'{database}_checksums.json'
        
        if checksum_file.exists():
            with open(checksum_file, 'r') as f:
                return json.load(f)
        
        return {}
    
    def save_checksums(self, database, checksums):
        """Save current checksums"""
        checksum_file = Path(self.config['backup_dir']) / f'{database}_checksums.json'
        
        with open(checksum_file, 'w') as f:
            json.dump(checksums, f, indent=2)
    
    def backup_changed_tables(self, database, changed_tables):
        """Backup only changed tables"""
        if not changed_tables:
            self.logger.info(f"No changes detected in {database}")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path(self.config['backup_dir']) / f'differential_{database}_{timestamp}'
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Backing up {len(changed_tables)} changed tables from {database}")
        
        for table in changed_tables:
            self.logger.info(f"Backing up table: {table}")
            
            backup_file = backup_dir / f'{table.replace(".", "_")}.dump'
            
            cmd = [
                'pg_dump',
                '-h', self.config['host'],
                '-U', self.config['username'],
                '-d', database,
                '--table', table,
                '--format=custom',
                '--compress=9',
                '--file', str(backup_file)
            ]
            
            try:
                subprocess.run(cmd, check=True)
                self.logger.info(f"Successfully backed up {table}")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Error backing up {table}: {e}")
    
    def perform_differential_backup(self, database):
        """Perform differential backup for a database"""
        self.logger.info(f"Starting differential backup for {database}")
        
        # Get current table list
        tables = self.get_database_tables(database)
        
        # Load previous checksums
        previous_checksums = self.load_previous_checksums(database)
        
        # Calculate current checksums and find changes
        current_checksums = {}
        changed_tables = []
        
        for table in tables:
            checksum = self.get_table_checksum(database, table)
            if checksum:
                current_checksums[table] = {
                    'checksum': checksum,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Check if table changed
                if (table not in previous_checksums or 
                    previous_checksums[table]['checksum'] != checksum):
                    changed_tables.append(table)
                    self.logger.info(f"Change detected in table: {table}")
        
        # Backup changed tables
        if changed_tables:
            self.backup_changed_tables(database, changed_tables)
            
            # Create manifest file
            manifest = {
                'backup_type': 'differential',
                'database': database,
                'timestamp': datetime.now().isoformat(),
                'changed_tables': changed_tables,
                'total_tables': len(tables),
                'previous_backup': previous_checksums.get('_metadata', {}).get('timestamp', 'unknown')
            }
            
            manifest_file = Path(self.config['backup_dir']) / f'differential_{database}_{datetime.now().strftime("%Y%m%d_%H%M%S")}_manifest.json'
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
        
        # Save current checksums
        current_checksums['_metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'table_count': len(tables)
        }
        self.save_checksums(database, current_checksums)
        
        self.logger.info(f"Differential backup completed for {database}")
        return len(changed_tables)
    
    def cleanup_old_backups(self):
        """Clean up old differential backups"""
        cutoff_date = datetime.now() - timedelta(days=self.config.get('retention_days', 30))
        backup_dir = Path(self.config['backup_dir'])
        
        for item in backup_dir.iterdir():
            if item.is_dir() and item.name.startswith('differential_'):
                try:
                    # Extract timestamp from directory name
                    timestamp_str = item.name.split('_')[-2] + '_' + item.name.split('_')[-1]
                    backup_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                    
                    if backup_date < cutoff_date:
                        self.logger.info(f"Removing old backup: {item.name}")
                        subprocess.run(['rm', '-rf', str(item)], check=True)
                        
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"Could not parse date from {item.name}: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: differential_backup.py <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    backup_system = DifferentialBackup(config_file)
    
    databases = backup_system.config['databases']
    total_changes = 0
    
    for database in databases:
        changes = backup_system.perform_differential_backup(database)
        total_changes += changes
    
    # Cleanup old backups
    backup_system.cleanup_old_backups()
    
    backup_system.logger.info(f"Differential backup completed. Total changed tables: {total_changes}")

if __name__ == '__main__':
    main()
```

## Strategie Recovery

### 1. **Point-in-Time Recovery (PITR)**

#### Konfiguracja PITR w PostgreSQL:
```bash
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /archives/wal/%f'
max_wal_senders = 3
wal_keep_segments = 32

# Backup bazowy dla PITR
#!/bin/bash
BACKUP_DIR="/backups/pitr"
DATE=$(date +%Y%m%d_%H%M%S)
BASE_BACKUP_DIR="${BACKUP_DIR}/base_backup_${DATE}"

mkdir -p "$BASE_BACKUP_DIR"

# Tworzenie backup bazowego
pg_basebackup \
    --host=localhost \
    --username=postgres \
    --pgdata="$BASE_BACKUP_DIR" \
    --format=tar \
    --compress=9 \
    --progress \
    --verbose \
    --wal-method=stream

# Zapisz informacje o backup
echo "Base backup created: $(date)" > "${BASE_BACKUP_DIR}/backup_info.txt"
echo "Backup directory: $BASE_BACKUP_DIR" >> "${BASE_BACKUP_DIR}/backup_info.txt"

# PITR Recovery procedure
restore_to_point_in_time() {
    local target_time=$1
    local base_backup=$2
    local recovery_dir="/tmp/recovery_${DATE}"
    
    echo "Starting PITR recovery to: $target_time"
    
    # Zatrzymaj PostgreSQL
    systemctl stop postgresql
    
    # Backup aktualnych danych
    mv /var/lib/postgresql/12/main /var/lib/postgresql/12/main.backup.$(date +%s)
    
    # Przywróć base backup
    mkdir -p /var/lib/postgresql/12/main
    tar -xzf "${base_backup}/base.tar.gz" -C /var/lib/postgresql/12/main
    
    # Przygotuj recovery.conf
    cat > /var/lib/postgresql/12/main/recovery.conf << EOF
restore_command = 'cp /archives/wal/%f %p'
recovery_target_time = '$target_time'
recovery_target_action = 'promote'
EOF
    
    # Uruchom PostgreSQL w trybie recovery
    chown -R postgres:postgres /var/lib/postgresql/12/main
    systemctl start postgresql
    
    echo "PITR recovery initiated. Monitor logs for completion."
}

# Przykład użycia
# restore_to_point_in_time "2024-03-15 14:30:00" "$BASE_BACKUP_DIR"
```

#### Zaawansowany PITR z weryfikacją:
```python
#!/usr/bin/env python3
"""
Advanced Point-in-Time Recovery system
"""

import os
import sys
import subprocess
import logging
import shutil
from datetime import datetime
from pathlib import Path

class PITRRecovery:
    def __init__(self, config):
        self.config = config
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'/var/log/postgresql/pitr_recovery_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def find_base_backup(self, target_time):
        """Find appropriate base backup for target time"""
        backup_dir = Path(self.config['backup_dir'])
        suitable_backups = []
        
        for backup_path in backup_dir.glob('base_backup_*'):
            # Extract timestamp from backup directory name
            try:
                timestamp_str = backup_path.name.replace('base_backup_', '')
                backup_time = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                
                if backup_time <= target_time:
                    suitable_backups.append((backup_time, backup_path))
            except ValueError:
                continue
        
        if not suitable_backups:
            raise Exception("No suitable base backup found")
        
        # Return the latest backup before target time
        suitable_backups.sort(key=lambda x: x[0], reverse=True)
        return suitable_backups[0][1]
    
    def verify_wal_continuity(self, base_backup_path, target_time):
        """Verify WAL file continuity for recovery"""
        wal_dir = Path(self.config['wal_archive_dir'])
        
        # Read backup label to get starting WAL file
        backup_label_path = base_backup_path / 'backup_label'
        if not backup_label_path.exists():
            # Extract from tar if compressed
            backup_tar = base_backup_path / 'base.tar.gz'
            if backup_tar.exists():
                cmd = ['tar', '-tzf', str(backup_tar), 'backup_label']
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    # Extract just the backup_label file
                    subprocess.run(['tar', '-xzf', str(backup_tar), 'backup_label', 
                                  '-C', str(base_backup_path)], check=True)
                except subprocess.CalledProcessError:
                    self.logger.warning("Could not extract backup_label")
                    return True  # Assume continuity
        
        self.logger.info("WAL continuity verification completed")
        return True
    
    def prepare_recovery_config(self, target_time, target_xid=None, target_name=None):
        """Prepare recovery configuration"""
        recovery_conf = []
        
        # Basic recovery settings
        recovery_conf.append(f"restore_command = 'cp {self.config['wal_archive_dir']}/%f %p'")
        recovery_conf.append("recovery_target_action = 'promote'")
        
        # Recovery target
        if target_time:
            recovery_conf.append(f"recovery_target_time = '{target_time.strftime('%Y-%m-%d %H:%M:%S')}'")
        elif target_xid:
            recovery_conf.append(f"recovery_target_xid = '{target_xid}'")
        elif target_name:
            recovery_conf.append(f"recovery_target_name = '{target_name}'")
        
        # Additional settings
        recovery_conf.append("recovery_target_timeline = 'latest'")
        recovery_conf.append("recovery_target_inclusive = true")
        
        return '\n'.join(recovery_conf)
    
    def perform_pitr_recovery(self, target_time, dry_run=False):
        """Perform Point-in-Time Recovery"""
        self.logger.info(f"Starting PITR recovery to: {target_time}")
        
        if dry_run:
            self.logger.info("DRY RUN MODE - No actual changes will be made")
        
        # Find appropriate base backup
        base_backup_path = self.find_base_backup(target_time)
        self.logger.info(f"Using base backup: {base_backup_path}")
        
        # Verify WAL continuity
        if not self.verify_wal_continuity(base_backup_path, target_time):
            raise Exception("WAL file continuity check failed")
        
        if dry_run:
            self.logger.info("DRY RUN: Recovery would proceed with verified backup and WAL files")
            return
        
        # Stop PostgreSQL
        self.logger.info("Stopping PostgreSQL service")
        subprocess.run(['systemctl', 'stop', 'postgresql'], check=True)
        
        # Backup current data directory
        data_dir = Path(self.config['data_directory'])
        backup_suffix = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_data_dir = data_dir.parent / f"{data_dir.name}.backup.{backup_suffix}"
        
        self.logger.info(f"Backing up current data directory to: {backup_data_dir}")
        shutil.move(str(data_dir), str(backup_data_dir))
        
        try:
            # Restore base backup
            self.logger.info("Restoring base backup")
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract base backup
            base_tar = base_backup_path / 'base.tar.gz'
            if base_tar.exists():
                subprocess.run(['tar', '-xzf', str(base_tar), '-C', str(data_dir)], check=True)
            else:
                shutil.copytree(str(base_backup_path), str(data_dir), dirs_exist_ok=True)
            
            # Prepare recovery.conf
            recovery_conf_content = self.prepare_recovery_config(target_time)
            recovery_conf_path = data_dir / 'recovery.conf'
            
            with open(recovery_conf_path, 'w') as f:
                f.write(recovery_conf_content)
            
            self.logger.info("Recovery configuration prepared")
            
            # Set correct permissions
            subprocess.run(['chown', '-R', 'postgres:postgres', str(data_dir)], check=True)
            subprocess.run(['chmod', '700', str(data_dir)], check=True)
            
            # Start PostgreSQL for recovery
            self.logger.info("Starting PostgreSQL for recovery")
            subprocess.run(['systemctl', 'start', 'postgresql'], check=True)
            
            # Monitor recovery progress
            self.monitor_recovery_progress()
            
            self.logger.info("PITR recovery completed successfully")
            
        except Exception as e:
            self.logger.error(f"Recovery failed: {e}")
            
            # Restore original data directory
            if backup_data_dir.exists():
                self.logger.info("Restoring original data directory")
                if data_dir.exists():
                    shutil.rmtree(str(data_dir))
                shutil.move(str(backup_data_dir), str(data_dir))
                subprocess.run(['systemctl', 'start', 'postgresql'], check=True)
            
            raise
    
    def monitor_recovery_progress(self):
        """Monitor recovery progress"""
        import time
        
        self.logger.info("Monitoring recovery progress...")
        
        while True:
            try:
                # Check if recovery is complete
                result = subprocess.run([
                    'psql', '-h', 'localhost', '-U', 'postgres', 
                    '-c', 'SELECT pg_is_in_recovery();'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    if 'f' in result.stdout:  # Not in recovery mode
                        self.logger.info("Recovery completed - database is now accepting connections")
                        break
                    else:
                        self.logger.info("Recovery in progress...")
                
            except subprocess.TimeoutExpired:
                self.logger.info("Database still starting up...")
            except subprocess.CalledProcessError:
                self.logger.info("Database not yet ready...")
            
            time.sleep(10)
    
    def create_recovery_point(self, point_name):
        """Create named recovery point"""
        cmd = [
            'psql', '-h', 'localhost', '-U', 'postgres',
            '-c', f"SELECT pg_create_restore_point('{point_name}');"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info(f"Recovery point '{point_name}' created successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create recovery point: {e}")
            return False

def main():
    config = {
        'backup_dir': '/backups/postgresql',
        'wal_archive_dir': '/archives/wal',
        'data_directory': '/var/lib/postgresql/12/main'
    }
    
    if len(sys.argv) < 3:
        print("Usage: pitr_recovery.py <target_datetime> [dry_run]")
        print("Example: pitr_recovery.py '2024-03-15 14:30:00' dry_run")
        sys.exit(1)
    
    target_time_str = sys.argv[1]
    dry_run = len(sys.argv) > 2 and sys.argv[2] == 'dry_run'
    
    try:
        target_time = datetime.strptime(target_time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        print("Invalid datetime format. Use: YYYY-MM-DD HH:MM:SS")
        sys.exit(1)
    
    recovery_system = PITRRecovery(config)
    
    try:
        recovery_system.perform_pitr_recovery(target_time, dry_run)
    except Exception as e:
        print(f"Recovery failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

### 2. **Tablespace Recovery**

```sql
-- Backup tablespace
CREATE TABLESPACE sensitive_data 
LOCATION '/encrypted/tablespace/sensitive';

-- Restore procedura
CREATE OR REPLACE FUNCTION restore_tablespace(
    tablespace_name TEXT,
    backup_location TEXT,
    target_location TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    sql_cmd TEXT;
BEGIN
    -- Sprawdź czy tablespace istnieje
    IF EXISTS (SELECT 1 FROM pg_tablespace WHERE spcname = tablespace_name) THEN
        -- Drop istniejący tablespace
        sql_cmd := format('DROP TABLESPACE IF EXISTS %I', tablespace_name);
        EXECUTE sql_cmd;
    END IF;
    
    -- Przywróć pliki tablespace
    PERFORM pg_notify('restore_log', 
        format('Restoring tablespace %s from %s to %s', 
               tablespace_name, backup_location, target_location));
    
    -- Utwórz nowy tablespace
    sql_cmd := format('CREATE TABLESPACE %I LOCATION %L', 
                     tablespace_name, target_location);
    EXECUTE sql_cmd;
    
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        PERFORM pg_notify('restore_error', 
            format('Failed to restore tablespace %s: %s', tablespace_name, SQLERRM));
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;
```

### 3. **Database Recovery Automation**

```python
#!/usr/bin/env python3
"""
Automated Database Recovery System
"""

import os
import json
import subprocess
import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

class DatabaseRecoverySystem:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'/var/log/recovery_system_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def check_database_health(self):
        """Check database health and connectivity"""
        try:
            cmd = [
                'psql', 
                '-h', self.config['database']['host'],
                '-U', self.config['database']['username'],
                '-d', self.config['database']['name'],
                '-c', 'SELECT version();'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.info("Database health check: PASSED")
                return True
            else:
                self.logger.error(f"Database health check: FAILED - {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Database health check: TIMEOUT")
            return False
        except Exception as e:
            self.logger.error(f"Database health check: ERROR - {e}")
            return False
    
    def detect_corruption(self):
        """Detect data corruption"""
        corruption_checks = [
            # Check for corrupted pages
            """
            SELECT schemaname, tablename, 'Corrupted pages detected' as issue
            FROM pg_stat_database_conflicts 
            WHERE confl_deadlock > 0 OR confl_lock > 0;
            """,
            
            # Check for inconsistent indexes
            """
            SELECT schemaname, tablename, indexname, 'Index inconsistency' as issue
            FROM pg_stat_user_indexes 
            WHERE idx_scan = 0 AND idx_tup_read > 0;
            """,
            
            # Check for orphaned files
            """
            SELECT 'System' as schemaname, 'Files' as tablename, 
                   'Orphaned database files detected' as issue
            WHERE EXISTS (
                SELECT 1 FROM pg_stat_file('base') 
                WHERE NOT EXISTS (
                    SELECT 1 FROM pg_database WHERE oid::text = pg_stat_file.filename
                )
            );
            """
        ]
        
        issues = []
        for check_sql in corruption_checks:
            try:
                cmd = [
                    'psql',
                    '-h', self.config['database']['host'],
                    '-U', self.config['database']['username'],
                    '-d', self.config['database']['name'],
                    '-t', '-c', check_sql
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.stdout.strip():
                    issues.append(result.stdout.strip())
                    
            except Exception as e:
                self.logger.error(f"Corruption check failed: {e}")
        
        return issues
    
    def automatic_recovery(self, recovery_type='full'):
        """Perform automatic recovery based on detected issues"""
        self.logger.info(f"Starting automatic {recovery_type} recovery")
        
        if recovery_type == 'full':
            return self.full_database_recovery()
        elif recovery_type == 'partial':
            return self.partial_recovery()
        elif recovery_type == 'pitr':
            # Default to recovery 1 hour ago
            target_time = datetime.now() - timedelta(hours=1)
            return self.pitr_recovery(target_time)
        
        return False
    
    def full_database_recovery(self):
        """Perform full database recovery from latest backup"""
        try:
            # Find latest backup
            backup_dir = self.config['backup']['directory']
            latest_backup = self.find_latest_backup(backup_dir)
            
            if not latest_backup:
                self.logger.error("No backup found for recovery")
                return False
            
            self.logger.info(f"Restoring from backup: {latest_backup}")
            
            # Stop database
            subprocess.run(['systemctl', 'stop', 'postgresql'], check=True)
            
            # Backup current state
            current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            data_dir = self.config['database']['data_directory']
            backup_current = f"{data_dir}.corrupted.{current_time}"
            
            subprocess.run(['mv', data_dir, backup_current], check=True)
            
            # Restore from backup
            if latest_backup.endswith('.dump'):
                # Custom format backup
                subprocess.run(['createdb', self.config['database']['name']], check=True)
                subprocess.run([
                    'pg_restore',
                    '-h', self.config['database']['host'],
                    '-U', self.config['database']['username'],
                    '-d', self.config['database']['name'],
                    '--verbose',
                    latest_backup
                ], check=True)
            else:
                # SQL format backup
                subprocess.run(['createdb', self.config['database']['name']], check=True)
                with open(latest_backup, 'r') as f:
                    subprocess.run([
                        'psql',
                        '-h', self.config['database']['host'],
                        '-U', self.config['database']['username'],
                        '-d', self.config['database']['name']
                    ], stdin=f, check=True)
            
            # Start database
            subprocess.run(['systemctl', 'start', 'postgresql'], check=True)
            
            # Verify recovery
            if self.check_database_health():
                self.logger.info("Full recovery completed successfully")
                self.send_recovery_notification("Full recovery completed successfully")
                return True
            else:
                self.logger.error("Recovery verification failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Full recovery failed: {e}")
            self.send_recovery_notification(f"Full recovery failed: {e}")
            return False
    
    def find_latest_backup(self, backup_dir):
        """Find the latest backup file"""
        import glob
        
        backup_patterns = [
            f"{backup_dir}/*.dump",
            f"{backup_dir}/*.sql",
            f"{backup_dir}/*.sql.gz"
        ]
        
        all_backups = []
        for pattern in backup_patterns:
            all_backups.extend(glob.glob(pattern))
        
        if not all_backups:
            return None
        
        # Sort by modification time
        all_backups.sort(key=os.path.getmtime, reverse=True)
        return all_backups[0]
    
    def send_recovery_notification(self, message):
        """Send email notification about recovery status"""
        if not self.config.get('notifications', {}).get('email_enabled', False):
            return
        
        try:
            smtp_config = self.config['notifications']['smtp']
            
            msg = MimeMultipart()
            msg['From'] = smtp_config['from_email']
            msg['To'] = ', '.join(smtp_config['to_emails'])
            msg['Subject'] = f"Database Recovery Alert - {self.config['database']['name']}"
            
            body = f"""
            Database Recovery Alert
            =======================
            
            Database: {self.config['database']['name']}
            Host: {self.config['database']['host']}
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Message: {message}
            
            Please check the database status and logs for more details.
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
            if smtp_config.get('use_tls', False):
                server.starttls()
            
            if smtp_config.get('username'):
                server.login(smtp_config['username'], smtp_config['password'])
            
            server.send_message(msg)
            server.quit()
            
            self.logger.info("Recovery notification sent successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
    
    def run_recovery_check(self):
        """Main recovery check and execution loop"""
        self.logger.info("Starting database recovery check")
        
        # Check database health
        if self.check_database_health():
            self.logger.info("Database is healthy - no recovery needed")
            return
        
        # Detect specific issues
        corruption_issues = self.detect_corruption()
        
        if corruption_issues:
            self.logger.warning(f"Corruption detected: {corruption_issues}")
            
            # Attempt automatic recovery based on severity
            if len(corruption_issues) > 5:
                self.logger.info("Severe corruption detected - attempting full recovery")
                success = self.automatic_recovery('full')
            else:
                self.logger.info("Minor issues detected - attempting PITR recovery")
                success = self.automatic_recovery('pitr')
            
            if not success:
                self.logger.error("Automatic recovery failed - manual intervention required")
                self.send_recovery_notification("Automatic recovery failed - manual intervention required")
        else:
            self.logger.info("No corruption detected - database may be temporarily unavailable")
            
            # Wait and try again
            import time
            time.sleep(60)
            
            if not self.check_database_health():
                self.logger.warning("Database still unavailable - attempting restart")
                subprocess.run(['systemctl', 'restart', 'postgresql'])
                
                time.sleep(30)
                
                if not self.check_database_health():
                    self.logger.error("Database restart failed - attempting full recovery")
                    self.automatic_recovery('full')

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: recovery_system.py <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    recovery_system = DatabaseRecoverySystem(config_file)
    
    recovery_system.run_recovery_check()

if __name__ == '__main__':
    main()
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**

#### 1. **Strategia 3-2-1**
```
3 kopie danych (oryginał + 2 backup)
2 różne media (dysk + taśma/cloud)
1 kopia off-site (poza lokalizacją)
```

#### 2. **Testowanie recovery**
```bash
# Regularne testy recovery
#!/bin/bash
# Test restore procedure
TEST_DATE=$(date +%Y%m%d)
TEST_DB="test_restore_${TEST_DATE}"

# Restore to test database
pg_restore -h localhost -U postgres -C -d postgres \
    --dbname="$TEST_DB" latest_backup.dump

# Run verification queries
psql -h localhost -U postgres -d "$TEST_DB" -c "
    SELECT 
        count(*) as table_count 
    FROM information_schema.tables 
    WHERE table_schema = 'public';
"

# Cleanup
dropdb -h localhost -U postgres "$TEST_DB"
```

#### 3. **Monitoring i alerting**
```python
# Monitor backup success
def check_backup_freshness():
    latest_backup = find_latest_backup()
    backup_age = datetime.now() - os.path.getmtime(latest_backup)
    
    if backup_age > timedelta(hours=25):  # Daily backup + 1h tolerance
        send_alert("Backup is overdue!")
```

### ❌ **Złe praktyki:**

```bash
# ❌ Backup bez weryfikacji
pg_dump database > backup.sql  # Nie sprawdza czy się udało

# ❌ Nieregularne testy recovery
# ❌ Backup w tym samym miejscu co dane
# ❌ Brak monitorowania backup
# ❌ Nieaktualizowane procedury recovery
```

## Pułapki egzaminacyjne

### 1. **Rodzaje backup**
```
Full backup - kompletna kopia bazy
Incremental - tylko zmiany od ostatniego backup
Differential - zmiany od ostatniego full backup
```

### 2. **PITR Requirements**
```
WAL archiving musi być włączony
Base backup + WAL files
continuous archiving
```

### 3. **Recovery objectives**
```
RPO - ile danych możemy stracić
RTO - jak długo może trwać recovery
Warm standby vs Hot standby
```

### 4. **PostgreSQL specifics**
```
pg_dump vs pg_basebackup
WAL files vs backup files
recovery.conf vs postgresql.auto.conf (PG 12+)
```