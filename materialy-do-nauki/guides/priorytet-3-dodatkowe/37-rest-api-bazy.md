# REST API w bazach danych

## Definicja REST API

**REST (Representational State Transfer)** to **architekturalny styl projektowania API** oparty na protokole HTTP, który umożliwia **dostęp do zasobów bazy danych** poprzez standardowe operacje HTTP.

### Kluczowe zasady REST:
- **Stateless** - każde żądanie zawiera wszystkie potrzebne informacje
- **Client-Server** - separation of concerns
- **Cacheable** - responses mogą być cache'owane
- **Uniform Interface** - standardowe metody HTTP
- **Layered System** - architektura warstwowa
- **Code on Demand** (opcjonalne) - możliwość przesyłania kodu

### HTTP Methods w REST:
```
GET    - pobieranie danych (READ)
POST   - tworzenie nowych zasobów (CREATE)
PUT    - aktualizacja całego zasobu (UPDATE)
PATCH  - częściowa aktualizacja (PARTIAL UPDATE)
DELETE - usuwanie zasobów (DELETE)
```

## Implementacja REST API dla baz danych

### 1. **Python Flask + SQLAlchemy**

#### Model danych:
```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/company_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Models
class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    budget = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    employees = db.relationship('Employee', backref='department', lazy=True, cascade='all, delete-orphan')

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    salary = db.Column(db.Float)
    hire_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# Schemas for serialization/validation
class DepartmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Department
        load_instance = True
        include_fk = True
    
    employees = ma.Nested('EmployeeSchema', many=True, exclude=['department'])

class EmployeeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Employee
        load_instance = True
        include_fk = True
    
    full_name = ma.Method('get_full_name')
    department = ma.Nested(DepartmentSchema, exclude=['employees'])
    
    def get_full_name(self, obj):
        return obj.full_name()

# Initialize schemas
department_schema = DepartmentSchema()
departments_schema = DepartmentSchema(many=True)
employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)
```

#### REST Endpoints:
```python
# Error handlers
@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({'error': 'Validation failed', 'messages': e.messages}), 400

@app.errorhandler(404)
def handle_not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def handle_internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# Department endpoints
@app.route('/api/departments', methods=['GET'])
def get_departments():
    """Get all departments with optional filtering"""
    try:
        # Query parameters for filtering
        name_filter = request.args.get('name')
        min_budget = request.args.get('min_budget', type=float)
        max_budget = request.args.get('max_budget', type=float)
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Build query
        query = Department.query
        
        if name_filter:
            query = query.filter(Department.name.ilike(f'%{name_filter}%'))
        if min_budget:
            query = query.filter(Department.budget >= min_budget)
        if max_budget:
            query = query.filter(Department.budget <= max_budget)
        
        # Execute paginated query
        departments = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = departments_schema.dump(departments.items)
        
        return jsonify({
            'departments': result,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': departments.total,
                'pages': departments.pages,
                'has_next': departments.has_next,
                'has_prev': departments.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/departments/<int:dept_id>', methods=['GET'])
def get_department(dept_id):
    """Get specific department by ID"""
    department = Department.query.get_or_404(dept_id)
    return jsonify(department_schema.dump(department))

@app.route('/api/departments', methods=['POST'])
def create_department():
    """Create new department"""
    try:
        # Validate and deserialize input
        department = department_schema.load(request.json)
        
        # Save to database
        db.session.add(department)
        db.session.commit()
        
        return jsonify(department_schema.dump(department)), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'messages': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/departments/<int:dept_id>', methods=['PUT'])
def update_department(dept_id):
    """Update entire department"""
    try:
        department = Department.query.get_or_404(dept_id)
        
        # Load and validate new data
        updated_data = department_schema.load(request.json, instance=department)
        
        db.session.commit()
        
        return jsonify(department_schema.dump(updated_data))
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'messages': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/departments/<int:dept_id>', methods=['PATCH'])
def patch_department(dept_id):
    """Partially update department"""
    try:
        department = Department.query.get_or_404(dept_id)
        
        # Update only provided fields
        if 'name' in request.json:
            department.name = request.json['name']
        if 'budget' in request.json:
            department.budget = request.json['budget']
        
        db.session.commit()
        
        return jsonify(department_schema.dump(department))
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/departments/<int:dept_id>', methods=['DELETE'])
def delete_department(dept_id):
    """Delete department"""
    try:
        department = Department.query.get_or_404(dept_id)
        
        # Check if department has employees
        if department.employees:
            return jsonify({
                'error': 'Cannot delete department with employees',
                'employee_count': len(department.employees)
            }), 400
        
        db.session.delete(department)
        db.session.commit()
        
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Employee endpoints
@app.route('/api/employees', methods=['GET'])
def get_employees():
    """Get all employees with filtering and sorting"""
    try:
        # Query parameters
        department_id = request.args.get('department_id', type=int)
        min_salary = request.args.get('min_salary', type=float)
        max_salary = request.args.get('max_salary', type=float)
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'id')
        sort_order = request.args.get('sort_order', 'asc')
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Build query
        query = Employee.query
        
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        if min_salary:
            query = query.filter(Employee.salary >= min_salary)
        if max_salary:
            query = query.filter(Employee.salary <= max_salary)
        if search:
            search_filter = f'%{search}%'
            query = query.filter(
                db.or_(
                    Employee.first_name.ilike(search_filter),
                    Employee.last_name.ilike(search_filter),
                    Employee.email.ilike(search_filter)
                )
            )
        
        # Sorting
        if hasattr(Employee, sort_by):
            sort_column = getattr(Employee, sort_by)
            if sort_order.lower() == 'desc':
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        
        # Execute query
        employees = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = employees_schema.dump(employees.items)
        
        return jsonify({
            'employees': result,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': employees.total,
                'pages': employees.pages
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees/<int:emp_id>', methods=['GET'])
def get_employee(emp_id):
    """Get specific employee by ID"""
    employee = Employee.query.get_or_404(emp_id)
    return jsonify(employee_schema.dump(employee))

@app.route('/api/employees', methods=['POST'])
def create_employee():
    """Create new employee"""
    try:
        employee = employee_schema.load(request.json)
        
        # Verify department exists if provided
        if employee.department_id:
            Department.query.get_or_404(employee.department_id)
        
        db.session.add(employee)
        db.session.commit()
        
        return jsonify(employee_schema.dump(employee)), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'messages': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees/<int:emp_id>', methods=['PUT'])
def update_employee(emp_id):
    """Update entire employee"""
    try:
        employee = Employee.query.get_or_404(emp_id)
        updated_employee = employee_schema.load(request.json, instance=employee)
        
        db.session.commit()
        
        return jsonify(employee_schema.dump(updated_employee))
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'messages': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees/<int:emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    """Delete employee"""
    try:
        employee = Employee.query.get_or_404(emp_id)
        db.session.delete(employee)
        db.session.commit()
        
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Advanced endpoints
@app.route('/api/departments/<int:dept_id>/employees', methods=['GET'])
def get_department_employees(dept_id):
    """Get all employees in specific department"""
    department = Department.query.get_or_404(dept_id)
    employees = Employee.query.filter_by(department_id=dept_id).all()
    
    return jsonify({
        'department': department_schema.dump(department),
        'employees': employees_schema.dump(employees)
    })

@app.route('/api/statistics/departments', methods=['GET'])
def get_department_statistics():
    """Get department statistics"""
    try:
        from sqlalchemy import func
        
        stats = db.session.query(
            Department.id,
            Department.name,
            func.count(Employee.id).label('employee_count'),
            func.avg(Employee.salary).label('avg_salary'),
            func.min(Employee.salary).label('min_salary'),
            func.max(Employee.salary).label('max_salary')
        ).outerjoin(Employee).group_by(Department.id, Department.name).all()
        
        result = []
        for stat in stats:
            result.append({
                'department_id': stat.id,
                'department_name': stat.name,
                'employee_count': stat.employee_count or 0,
                'avg_salary': float(stat.avg_salary) if stat.avg_salary else 0,
                'min_salary': float(stat.min_salary) if stat.min_salary else 0,
                'max_salary': float(stat.max_salary) if stat.max_salary else 0
            })
        
        return jsonify({'department_statistics': result})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Batch operations
@app.route('/api/employees/batch', methods=['POST'])
def create_employees_batch():
    """Create multiple employees at once"""
    try:
        if not isinstance(request.json, list):
            return jsonify({'error': 'Expected array of employees'}), 400
        
        employees = employees_schema.load(request.json)
        
        for employee in employees:
            db.session.add(employee)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Created {len(employees)} employees',
            'employees': employees_schema.dump(employees)
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'messages': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

### 2. **Node.js Express + Sequelize**

#### Model definition:
```javascript
const express = require('express');
const { Sequelize, DataTypes } = require('sequelize');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Database connection
const sequelize = new Sequelize('postgresql://user:password@localhost:5432/company_db', {
    logging: console.log, // Set to false in production
    pool: {
        max: 10,
        min: 0,
        acquire: 30000,
        idle: 10000
    }
});

// Models
const Department = sequelize.define('Department', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    name: {
        type: DataTypes.STRING(100),
        allowNull: false,
        unique: true,
        validate: {
            notEmpty: true,
            len: [2, 100]
        }
    },
    budget: {
        type: DataTypes.FLOAT,
        validate: {
            min: 0
        }
    }
}, {
    tableName: 'departments',
    timestamps: true
});

const Employee = sequelize.define('Employee', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    firstName: {
        type: DataTypes.STRING(50),
        allowNull: false,
        field: 'first_name',
        validate: {
            notEmpty: true,
            len: [2, 50]
        }
    },
    lastName: {
        type: DataTypes.STRING(50),
        allowNull: false,
        field: 'last_name',
        validate: {
            notEmpty: true,
            len: [2, 50]
        }
    },
    email: {
        type: DataTypes.STRING(100),
        allowNull: false,
        unique: true,
        validate: {
            isEmail: true
        }
    },
    salary: {
        type: DataTypes.FLOAT,
        validate: {
            min: 0
        }
    },
    hireDate: {
        type: DataTypes.DATE,
        field: 'hire_date',
        defaultValue: DataTypes.NOW
    }
}, {
    tableName: 'employees',
    timestamps: true
});

// Associations
Department.hasMany(Employee, { foreignKey: 'departmentId', as: 'employees' });
Employee.belongsTo(Department, { foreignKey: 'departmentId', as: 'department' });
```

#### REST Endpoints:
```javascript
// Error handling middleware
const handleError = (res, error) => {
    console.error(error);
    
    if (error.name === 'SequelizeValidationError') {
        return res.status(400).json({
            error: 'Validation failed',
            messages: error.errors.map(e => ({
                field: e.path,
                message: e.message
            }))
        });
    }
    
    if (error.name === 'SequelizeUniqueConstraintError') {
        return res.status(409).json({
            error: 'Resource already exists',
            field: error.errors[0].path
        });
    }
    
    return res.status(500).json({ error: 'Internal server error' });
};

// Department routes
app.get('/api/departments', async (req, res) => {
    try {
        const { page = 1, limit = 10, name, minBudget, maxBudget } = req.query;
        const offset = (page - 1) * limit;
        
        const where = {};
        if (name) {
            where.name = { [Sequelize.Op.iLike]: `%${name}%` };
        }
        if (minBudget) {
            where.budget = { [Sequelize.Op.gte]: parseFloat(minBudget) };
        }
        if (maxBudget) {
            where.budget = { ...where.budget, [Sequelize.Op.lte]: parseFloat(maxBudget) };
        }
        
        const { count, rows } = await Department.findAndCountAll({
            where,
            include: [{
                model: Employee,
                as: 'employees',
                attributes: ['id', 'firstName', 'lastName', 'email']
            }],
            limit: parseInt(limit),
            offset: parseInt(offset),
            order: [['name', 'ASC']]
        });
        
        res.json({
            departments: rows,
            pagination: {
                page: parseInt(page),
                limit: parseInt(limit),
                total: count,
                pages: Math.ceil(count / limit)
            }
        });
    } catch (error) {
        handleError(res, error);
    }
});

app.get('/api/departments/:id', async (req, res) => {
    try {
        const department = await Department.findByPk(req.params.id, {
            include: [{
                model: Employee,
                as: 'employees'
            }]
        });
        
        if (!department) {
            return res.status(404).json({ error: 'Department not found' });
        }
        
        res.json(department);
    } catch (error) {
        handleError(res, error);
    }
});

app.post('/api/departments', async (req, res) => {
    try {
        const department = await Department.create(req.body);
        res.status(201).json(department);
    } catch (error) {
        handleError(res, error);
    }
});

app.put('/api/departments/:id', async (req, res) => {
    try {
        const department = await Department.findByPk(req.params.id);
        
        if (!department) {
            return res.status(404).json({ error: 'Department not found' });
        }
        
        await department.update(req.body);
        res.json(department);
    } catch (error) {
        handleError(res, error);
    }
});

app.delete('/api/departments/:id', async (req, res) => {
    try {
        const department = await Department.findByPk(req.params.id, {
            include: [{ model: Employee, as: 'employees' }]
        });
        
        if (!department) {
            return res.status(404).json({ error: 'Department not found' });
        }
        
        if (department.employees.length > 0) {
            return res.status(400).json({
                error: 'Cannot delete department with employees',
                employeeCount: department.employees.length
            });
        }
        
        await department.destroy();
        res.status(204).send();
    } catch (error) {
        handleError(res, error);
    }
});

// Employee routes
app.get('/api/employees', async (req, res) => {
    try {
        const { 
            page = 1, 
            limit = 10, 
            departmentId, 
            minSalary, 
            maxSalary, 
            search,
            sortBy = 'id',
            sortOrder = 'ASC'
        } = req.query;
        
        const offset = (page - 1) * limit;
        const where = {};
        
        if (departmentId) {
            where.departmentId = departmentId;
        }
        if (minSalary) {
            where.salary = { [Sequelize.Op.gte]: parseFloat(minSalary) };
        }
        if (maxSalary) {
            where.salary = { ...where.salary, [Sequelize.Op.lte]: parseFloat(maxSalary) };
        }
        if (search) {
            where[Sequelize.Op.or] = [
                { firstName: { [Sequelize.Op.iLike]: `%${search}%` } },
                { lastName: { [Sequelize.Op.iLike]: `%${search}%` } },
                { email: { [Sequelize.Op.iLike]: `%${search}%` } }
            ];
        }
        
        const { count, rows } = await Employee.findAndCountAll({
            where,
            include: [{
                model: Department,
                as: 'department',
                attributes: ['id', 'name']
            }],
            limit: parseInt(limit),
            offset: parseInt(offset),
            order: [[sortBy, sortOrder.toUpperCase()]]
        });
        
        res.json({
            employees: rows,
            pagination: {
                page: parseInt(page),
                limit: parseInt(limit),
                total: count,
                pages: Math.ceil(count / limit)
            }
        });
    } catch (error) {
        handleError(res, error);
    }
});

// Statistics endpoint
app.get('/api/statistics/departments', async (req, res) => {
    try {
        const stats = await Department.findAll({
            attributes: [
                'id',
                'name',
                [Sequelize.fn('COUNT', Sequelize.col('employees.id')), 'employeeCount'],
                [Sequelize.fn('AVG', Sequelize.col('employees.salary')), 'avgSalary'],
                [Sequelize.fn('MIN', Sequelize.col('employees.salary')), 'minSalary'],
                [Sequelize.fn('MAX', Sequelize.col('employees.salary')), 'maxSalary']
            ],
            include: [{
                model: Employee,
                as: 'employees',
                attributes: []
            }],
            group: ['Department.id'],
            raw: true
        });
        
        res.json({ departmentStatistics: stats });
    } catch (error) {
        handleError(res, error);
    }
});

// Batch operations
app.post('/api/employees/batch', async (req, res) => {
    const transaction = await sequelize.transaction();
    
    try {
        if (!Array.isArray(req.body)) {
            return res.status(400).json({ error: 'Expected array of employees' });
        }
        
        const employees = await Employee.bulkCreate(req.body, {
            validate: true,
            transaction
        });
        
        await transaction.commit();
        
        res.status(201).json({
            message: `Created ${employees.length} employees`,
            employees
        });
    } catch (error) {
        await transaction.rollback();
        handleError(res, error);
    }
});

// Start server
const PORT = process.env.PORT || 3000;

sequelize.authenticate()
    .then(() => {
        console.log('Database connected successfully');
        return sequelize.sync({ alter: true });
    })
    .then(() => {
        app.listen(PORT, () => {
            console.log(`Server running on port ${PORT}`);
        });
    })
    .catch(error => {
        console.error('Unable to connect to database:', error);
    });
```

### 3. **Java Spring Boot + JPA**

#### Entity definition:
```java
// Department.java
@Entity
@Table(name = "departments")
public class Department {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true, length = 100)
    @NotBlank(message = "Department name is required")
    @Size(min = 2, max = 100, message = "Department name must be between 2 and 100 characters")
    private String name;
    
    @Min(value = 0, message = "Budget must be positive")
    private Double budget;
    
    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @OneToMany(mappedBy = "department", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @JsonManagedReference
    private List<Employee> employees = new ArrayList<>();
    
    // Constructors, getters, setters
}

// Employee.java
@Entity
@Table(name = "employees")
public class Employee {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "first_name", nullable = false, length = 50)
    @NotBlank(message = "First name is required")
    private String firstName;
    
    @Column(name = "last_name", nullable = false, length = 50)
    @NotBlank(message = "Last name is required")
    private String lastName;
    
    @Column(unique = true, nullable = false, length = 100)
    @Email(message = "Email should be valid")
    @NotBlank(message = "Email is required")
    private String email;
    
    @Min(value = 0, message = "Salary must be positive")
    private Double salary;
    
    @Column(name = "hire_date")
    private LocalDateTime hireDate = LocalDateTime.now();
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "department_id")
    @JsonBackReference
    private Department department;
    
    // Constructors, getters, setters
    
    @JsonProperty("fullName")
    public String getFullName() {
        return firstName + " " + lastName;
    }
}
```

#### Repository interfaces:
```java
// DepartmentRepository.java
@Repository
public interface DepartmentRepository extends JpaRepository<Department, Long> {
    
    @Query("SELECT d FROM Department d WHERE " +
           "(:name IS NULL OR LOWER(d.name) LIKE LOWER(CONCAT('%', :name, '%'))) AND " +
           "(:minBudget IS NULL OR d.budget >= :minBudget) AND " +
           "(:maxBudget IS NULL OR d.budget <= :maxBudget)")
    Page<Department> findDepartmentsWithFilters(
        @Param("name") String name,
        @Param("minBudget") Double minBudget,
        @Param("maxBudget") Double maxBudget,
        Pageable pageable
    );
    
    @Query("SELECT new com.example.dto.DepartmentStatsDto(" +
           "d.id, d.name, COUNT(e.id), AVG(e.salary), MIN(e.salary), MAX(e.salary)) " +
           "FROM Department d LEFT JOIN d.employees e " +
           "GROUP BY d.id, d.name")
    List<DepartmentStatsDto> getDepartmentStatistics();
}

// EmployeeRepository.java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {
    
    @Query("SELECT e FROM Employee e WHERE " +
           "(:departmentId IS NULL OR e.department.id = :departmentId) AND " +
           "(:minSalary IS NULL OR e.salary >= :minSalary) AND " +
           "(:maxSalary IS NULL OR e.salary <= :maxSalary) AND " +
           "(:search IS NULL OR LOWER(e.firstName) LIKE LOWER(CONCAT('%', :search, '%')) OR " +
           " LOWER(e.lastName) LIKE LOWER(CONCAT('%', :search, '%')) OR " +
           " LOWER(e.email) LIKE LOWER(CONCAT('%', :search, '%')))")
    Page<Employee> findEmployeesWithFilters(
        @Param("departmentId") Long departmentId,
        @Param("minSalary") Double minSalary,
        @Param("maxSalary") Double maxSalary,
        @Param("search") String search,
        Pageable pageable
    );
}
```

#### REST Controller:
```java
@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
@Validated
public class CompanyController {
    
    @Autowired
    private DepartmentRepository departmentRepository;
    
    @Autowired
    private EmployeeRepository employeeRepository;
    
    // Exception handlers
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidationExceptions(
            MethodArgumentNotValidException ex) {
        Map<String, Object> errors = new HashMap<>();
        Map<String, String> fieldErrors = new HashMap<>();
        
        ex.getBindingResult().getFieldErrors().forEach(error -> 
            fieldErrors.put(error.getField(), error.getDefaultMessage())
        );
        
        errors.put("error", "Validation failed");
        errors.put("messages", fieldErrors);
        
        return ResponseEntity.badRequest().body(errors);
    }
    
    @ExceptionHandler(DataIntegrityViolationException.class)
    public ResponseEntity<Map<String, String>> handleDataIntegrityViolation(
            DataIntegrityViolationException ex) {
        Map<String, String> error = new HashMap<>();
        error.put("error", "Data integrity violation");
        return ResponseEntity.status(HttpStatus.CONFLICT).body(error);
    }
    
    // Department endpoints
    @GetMapping("/departments")
    public ResponseEntity<Map<String, Object>> getDepartments(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "name") String sortBy,
            @RequestParam(defaultValue = "asc") String sortDir,
            @RequestParam(required = false) String name,
            @RequestParam(required = false) Double minBudget,
            @RequestParam(required = false) Double maxBudget) {
        
        Sort sort = sortDir.equalsIgnoreCase("desc") ? 
                   Sort.by(sortBy).descending() : 
                   Sort.by(sortBy).ascending();
        
        Pageable pageable = PageRequest.of(page, size, sort);
        
        Page<Department> departmentPage = departmentRepository.findDepartmentsWithFilters(
            name, minBudget, maxBudget, pageable
        );
        
        Map<String, Object> response = new HashMap<>();
        response.put("departments", departmentPage.getContent());
        
        Map<String, Object> pagination = new HashMap<>();
        pagination.put("page", page);
        pagination.put("size", size);
        pagination.put("total", departmentPage.getTotalElements());
        pagination.put("pages", departmentPage.getTotalPages());
        pagination.put("hasNext", departmentPage.hasNext());
        pagination.put("hasPrev", departmentPage.hasPrevious());
        
        response.put("pagination", pagination);
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/departments/{id}")
    public ResponseEntity<Department> getDepartment(@PathVariable Long id) {
        Optional<Department> department = departmentRepository.findById(id);
        return department.map(ResponseEntity::ok)
                        .orElse(ResponseEntity.notFound().build());
    }
    
    @PostMapping("/departments")
    public ResponseEntity<Department> createDepartment(@Valid @RequestBody Department department) {
        Department savedDepartment = departmentRepository.save(department);
        return ResponseEntity.status(HttpStatus.CREATED).body(savedDepartment);
    }
    
    @PutMapping("/departments/{id}")
    public ResponseEntity<Department> updateDepartment(
            @PathVariable Long id, 
            @Valid @RequestBody Department departmentDetails) {
        
        Optional<Department> optionalDepartment = departmentRepository.findById(id);
        
        if (optionalDepartment.isPresent()) {
            Department department = optionalDepartment.get();
            department.setName(departmentDetails.getName());
            department.setBudget(departmentDetails.getBudget());
            
            Department updatedDepartment = departmentRepository.save(department);
            return ResponseEntity.ok(updatedDepartment);
        } else {
            return ResponseEntity.notFound().build();
        }
    }
    
    @DeleteMapping("/departments/{id}")
    public ResponseEntity<?> deleteDepartment(@PathVariable Long id) {
        Optional<Department> optionalDepartment = departmentRepository.findById(id);
        
        if (optionalDepartment.isPresent()) {
            Department department = optionalDepartment.get();
            
            if (!department.getEmployees().isEmpty()) {
                Map<String, Object> error = new HashMap<>();
                error.put("error", "Cannot delete department with employees");
                error.put("employeeCount", department.getEmployees().size());
                return ResponseEntity.badRequest().body(error);
            }
            
            departmentRepository.delete(department);
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
    
    // Statistics endpoint
    @GetMapping("/statistics/departments")
    public ResponseEntity<Map<String, Object>> getDepartmentStatistics() {
        List<DepartmentStatsDto> stats = departmentRepository.getDepartmentStatistics();
        
        Map<String, Object> response = new HashMap<>();
        response.put("departmentStatistics", stats);
        
        return ResponseEntity.ok(response);
    }
    
    // Batch operations
    @PostMapping("/employees/batch")
    @Transactional
    public ResponseEntity<Map<String, Object>> createEmployeesBatch(
            @Valid @RequestBody List<Employee> employees) {
        
        List<Employee> savedEmployees = employeeRepository.saveAll(employees);
        
        Map<String, Object> response = new HashMap<>();
        response.put("message", "Created " + savedEmployees.size() + " employees");
        response.put("employees", savedEmployees);
        
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
}
```

## API Documentation i testowanie

### 1. **OpenAPI/Swagger Documentation**

#### Python Flask:
```python
from flask import Flask
from flask_restx import Api, Resource, fields
from flask_restx import reqparse

app = Flask(__name__)
api = Api(app, doc='/docs/', title='Company API', description='REST API for company management')

# Namespaces
departments_ns = api.namespace('departments', description='Department operations')
employees_ns = api.namespace('employees', description='Employee operations')

# Models for documentation
department_model = api.model('Department', {
    'id': fields.Integer(readonly=True, description='Department ID'),
    'name': fields.String(required=True, description='Department name'),
    'budget': fields.Float(description='Department budget'),
    'created_at': fields.DateTime(readonly=True),
    'employees': fields.List(fields.Nested('Employee'), readonly=True)
})

employee_model = api.model('Employee', {
    'id': fields.Integer(readonly=True, description='Employee ID'),
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'email': fields.String(required=True, description='Email address'),
    'salary': fields.Float(description='Salary'),
    'department_id': fields.Integer(description='Department ID'),
    'hire_date': fields.DateTime(readonly=True)
})

# Documented endpoints
@departments_ns.route('/')
class DepartmentList(Resource):
    @api.doc('list_departments')
    @api.marshal_list_with(department_model)
    @api.param('page', 'Page number', type='integer', default=1)
    @api.param('per_page', 'Items per page', type='integer', default=10)
    @api.param('name', 'Filter by name', type='string')
    def get(self):
        """Get all departments"""
        # Implementation
        pass
    
    @api.doc('create_department')
    @api.expect(department_model)
    @api.marshal_with(department_model, code=201)
    def post(self):
        """Create a new department"""
        # Implementation
        pass

@departments_ns.route('/<int:id>')
@api.response(404, 'Department not found')
@api.param('id', 'Department ID')
class Department(Resource):
    @api.doc('get_department')
    @api.marshal_with(department_model)
    def get(self, id):
        """Get department by ID"""
        # Implementation
        pass
    
    @api.doc('update_department')
    @api.expect(department_model)
    @api.marshal_with(department_model)
    def put(self, id):
        """Update department"""
        # Implementation
        pass
    
    @api.doc('delete_department')
    @api.response(204, 'Department deleted')
    def delete(self, id):
        """Delete department"""
        # Implementation
        pass
```

#### Java Spring Boot:
```java
@RestController
@RequestMapping("/api")
@Tag(name = "Company API", description = "REST API for company management")
public class CompanyController {
    
    @Operation(summary = "Get all departments", 
               description = "Retrieve a paginated list of departments with optional filtering")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Successful operation",
                    content = @Content(schema = @Schema(implementation = DepartmentPageResponse.class))),
        @ApiResponse(responseCode = "400", description = "Invalid parameters")
    })
    @GetMapping("/departments")
    public ResponseEntity<Map<String, Object>> getDepartments(
            @Parameter(description = "Page number (0-based)") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Page size") @RequestParam(defaultValue = "10") int size,
            @Parameter(description = "Sort field") @RequestParam(defaultValue = "name") String sortBy,
            @Parameter(description = "Sort direction") @RequestParam(defaultValue = "asc") String sortDir,
            @Parameter(description = "Filter by name") @RequestParam(required = false) String name,
            @Parameter(description = "Minimum budget") @RequestParam(required = false) Double minBudget,
            @Parameter(description = "Maximum budget") @RequestParam(required = false) Double maxBudget) {
        // Implementation
    }
    
    @Operation(summary = "Create new department")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "201", description = "Department created"),
        @ApiResponse(responseCode = "400", description = "Validation error"),
        @ApiResponse(responseCode = "409", description = "Department already exists")
    })
    @PostMapping("/departments")
    public ResponseEntity<Department> createDepartment(
            @Valid @RequestBody 
            @io.swagger.v3.oas.annotations.parameters.RequestBody(
                description = "Department to create",
                required = true,
                content = @Content(schema = @Schema(implementation = Department.class))
            ) Department department) {
        // Implementation
    }
}
```

### 2. **API Testing**

#### Unit tests (Python pytest):
```python
import pytest
from app import app, db, Department, Employee

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def sample_department(client):
    with app.app_context():
        dept = Department(name='IT', budget=100000)
        db.session.add(dept)
        db.session.commit()
        return dept

def test_get_departments_empty(client):
    """Test getting departments when none exist"""
    response = client.get('/api/departments')
    assert response.status_code == 200
    data = response.get_json()
    assert data['departments'] == []

def test_create_department(client):
    """Test creating a new department"""
    dept_data = {
        'name': 'HR',
        'budget': 80000
    }
    response = client.post('/api/departments', json=dept_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'HR'
    assert data['budget'] == 80000

def test_create_department_validation_error(client):
    """Test validation error when creating department"""
    dept_data = {
        'name': '',  # Empty name should fail validation
        'budget': 80000
    }
    response = client.post('/api/departments', json=dept_data)
    assert response.status_code == 400

def test_get_department_by_id(client, sample_department):
    """Test getting specific department"""
    response = client.get(f'/api/departments/{sample_department.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'IT'

def test_update_department(client, sample_department):
    """Test updating department"""
    update_data = {
        'name': 'Information Technology',
        'budget': 120000
    }
    response = client.put(f'/api/departments/{sample_department.id}', json=update_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Information Technology'
    assert data['budget'] == 120000

def test_delete_department(client, sample_department):
    """Test deleting department"""
    response = client.delete(f'/api/departments/{sample_department.id}')
    assert response.status_code == 204
    
    # Verify it's gone
    response = client.get(f'/api/departments/{sample_department.id}')
    assert response.status_code == 404

def test_pagination(client):
    """Test pagination"""
    # Create multiple departments
    with app.app_context():
        for i in range(15):
            dept = Department(name=f'Dept{i}', budget=1000 * i)
            db.session.add(dept)
        db.session.commit()
    
    # Test first page
    response = client.get('/api/departments?page=1&per_page=10')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['departments']) == 10
    assert data['pagination']['page'] == 1
    assert data['pagination']['total'] == 15

def test_filtering(client):
    """Test filtering departments"""
    with app.app_context():
        dept1 = Department(name='IT', budget=100000)
        dept2 = Department(name='HR', budget=50000)
        dept3 = Department(name='Finance', budget=80000)
        db.session.add_all([dept1, dept2, dept3])
        db.session.commit()
    
    # Test budget filtering
    response = client.get('/api/departments?min_budget=75000')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['departments']) == 2  # IT and Finance
```

#### Integration tests (Postman/Newman):
```json
{
    "info": {
        "name": "Company API Tests",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "Create Department",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 201', function () {",
                            "    pm.response.to.have.status(201);",
                            "});",
                            "",
                            "pm.test('Response has required fields', function () {",
                            "    const jsonData = pm.response.json();",
                            "    pm.expect(jsonData).to.have.property('id');",
                            "    pm.expect(jsonData).to.have.property('name');",
                            "    pm.expect(jsonData.name).to.eql('IT');",
                            "});",
                            "",
                            "// Store department ID for later tests",
                            "pm.globals.set('departmentId', pm.response.json().id);"
                        ]
                    }
                }
            ],
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\"name\": \"IT\", \"budget\": 100000}"
                },
                "url": {
                    "raw": "{{baseUrl}}/api/departments",
                    "host": ["{{baseUrl}}"],
                    "path": ["api", "departments"]
                }
            }
        },
        {
            "name": "Get Department",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 200', function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "",
                            "pm.test('Department data is correct', function () {",
                            "    const jsonData = pm.response.json();",
                            "    pm.expect(jsonData.name).to.eql('IT');",
                            "    pm.expect(jsonData.budget).to.eql(100000);",
                            "});"
                        ]
                    }
                }
            ],
            "request": {
                "method": "GET",
                "url": {
                    "raw": "{{baseUrl}}/api/departments/{{departmentId}}",
                    "host": ["{{baseUrl}}"],
                    "path": ["api", "departments", "{{departmentId}}"]
                }
            }
        }
    ],
    "variable": [
        {
            "key": "baseUrl",
            "value": "http://localhost:5000"
        }
    ]
}
```

## Performance i Security

### 1. **Rate Limiting**

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/departments', methods=['GET'])
@limiter.limit("100 per minute")
def get_departments():
    # Implementation
    pass

@app.route('/api/departments', methods=['POST'])
@limiter.limit("10 per minute")
def create_department():
    # Implementation
    pass
```

### 2. **API Versioning**

```python
# URL versioning
@app.route('/api/v1/departments', methods=['GET'])
def get_departments_v1():
    # Version 1 implementation
    pass

@app.route('/api/v2/departments', methods=['GET'])
def get_departments_v2():
    # Version 2 implementation with additional features
    pass

# Header versioning
@app.route('/api/departments', methods=['GET'])
def get_departments():
    version = request.headers.get('API-Version', 'v1')
    if version == 'v2':
        return get_departments_v2_logic()
    else:
        return get_departments_v1_logic()
```

### 3. **Caching**

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/api/departments/<int:dept_id>', methods=['GET'])
@cache.cached(timeout=300, key_prefix='dept_%s')
def get_department(dept_id):
    # Cached for 5 minutes
    department = Department.query.get_or_404(dept_id)
    return jsonify(department_schema.dump(department))

# Cache invalidation
@app.route('/api/departments/<int:dept_id>', methods=['PUT'])
def update_department(dept_id):
    # Update logic
    cache.delete(f'dept_{dept_id}')  # Invalidate cache
    return jsonify(result)
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**

#### 1. **REST Conventions**
```
GET /api/departments           - List all departments
GET /api/departments/123       - Get specific department  
POST /api/departments          - Create new department
PUT /api/departments/123       - Update entire department
PATCH /api/departments/123     - Partial update
DELETE /api/departments/123    - Delete department
```

#### 2. **HTTP Status Codes**
```
200 OK - Successful GET, PUT, PATCH
201 Created - Successful POST
204 No Content - Successful DELETE
400 Bad Request - Validation error
401 Unauthorized - Authentication required
403 Forbidden - Access denied
404 Not Found - Resource doesn't exist
409 Conflict - Resource already exists
500 Internal Server Error - Server error
```

#### 3. **Error Handling**
```json
{
    "error": "Validation failed",
    "messages": {
        "name": "Name is required",
        "email": "Invalid email format"
    },
    "timestamp": "2024-03-15T10:30:00Z",
    "path": "/api/employees"
}
```

### ❌ **Złe praktyki:**

```
❌ GET /api/getDepartments      - Nie używaj czasowników w URL
❌ POST /api/departments/delete - Użyj DELETE method
❌ Zwracanie 200 dla błędów     - Używaj odpowiednich kodów HTTP
❌ Brak walidacji danych        - Zawsze waliduj input
❌ Eksponowanie wewnętrznych błędów - Filtruj informacje o błędach
```

## Pułapki egzaminacyjne

### 1. **REST Principles**
```
REST jest stateless - każde żądanie zawiera wszystkie potrzebne dane
HTTP methods mają semantykę - GET (safe), PUT (idempotent)
Resource-based URLs - rzeczowniki, nie czasowniki
```

### 2. **HTTP Status Codes**
```
2xx - Success (200, 201, 204)
4xx - Client Error (400, 401, 404, 409)
5xx - Server Error (500, 503)
```

### 3. **Content Negotiation**
```
Accept: application/json - klient określa format odpowiedzi
Content-Type: application/json - serwer określa format żądania
```

### 4. **Idempotency**
```
GET, PUT, DELETE - idempotent (można bezpiecznie powtarzać)
POST - nie-idempotent (każde wywołanie może mieć różny efekt)
```