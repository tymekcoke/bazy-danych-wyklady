# Integracja baz danych z aplikacjami

## Definicja integracji

**Integracja baz danych z aplikacjami** to proces **łączenia warstwy danych z logiką aplikacyjną** w sposób efektywny, bezpieczny i skalowalny.

### Kluczowe aspekty:
- **Separation of Concerns** - oddzielenie logiki biznesowej od danych
- **Data Access Layer** - warstwa dostępu do danych
- **Connection Management** - zarządzanie połączeniami
- **Transaction Management** - zarządzanie transakcjami
- **Error Handling** - obsługa błędów
- **Performance Optimization** - optymalizacja wydajności

### Wzorce architektoniczne:
- **DAO (Data Access Object)** - enkapsulacja dostępu do danych
- **Repository Pattern** - abstrakcja nad warstwą danych
- **Active Record** - obiekty zawierające logikę dostępu
- **Data Mapper** - mapowanie obiektów na dane

## Wzorce dostępu do danych

### 1. **DAO (Data Access Object)**

#### Java implementation:
```java
// Interface DAO
public interface EmployeeDAO {
    void save(Employee employee);
    Employee findById(Long id);
    List<Employee> findAll();
    List<Employee> findByDepartment(String department);
    void update(Employee employee);
    void delete(Long id);
    List<Employee> findBySalaryRange(Double minSalary, Double maxSalary);
}

// Implementation
@Repository
public class EmployeeDAOImpl implements EmployeeDAO {
    
    @Autowired
    private JdbcTemplate jdbcTemplate;
    
    private final RowMapper<Employee> employeeRowMapper = (rs, rowNum) -> {
        Employee employee = new Employee();
        employee.setId(rs.getLong("id"));
        employee.setFirstName(rs.getString("first_name"));
        employee.setLastName(rs.getString("last_name"));
        employee.setEmail(rs.getString("email"));
        employee.setSalary(rs.getDouble("salary"));
        employee.setDepartment(rs.getString("department"));
        employee.setHireDate(rs.getTimestamp("hire_date").toLocalDateTime());
        return employee;
    };
    
    @Override
    public void save(Employee employee) {
        String sql = "INSERT INTO employees (first_name, last_name, email, salary, department) " +
                    "VALUES (?, ?, ?, ?, ?)";
        
        KeyHolder keyHolder = new GeneratedKeyHolder();
        
        jdbcTemplate.update(connection -> {
            PreparedStatement ps = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setString(1, employee.getFirstName());
            ps.setString(2, employee.getLastName());
            ps.setString(3, employee.getEmail());
            ps.setDouble(4, employee.getSalary());
            ps.setString(5, employee.getDepartment());
            return ps;
        }, keyHolder);
        
        employee.setId(keyHolder.getKey().longValue());
    }
    
    @Override
    public Employee findById(Long id) {
        String sql = "SELECT * FROM employees WHERE id = ?";
        try {
            return jdbcTemplate.queryForObject(sql, employeeRowMapper, id);
        } catch (EmptyResultDataAccessException e) {
            return null;
        }
    }
    
    @Override
    public List<Employee> findAll() {
        String sql = "SELECT * FROM employees ORDER BY last_name, first_name";
        return jdbcTemplate.query(sql, employeeRowMapper);
    }
    
    @Override
    public List<Employee> findByDepartment(String department) {
        String sql = "SELECT * FROM employees WHERE department = ? ORDER BY salary DESC";
        return jdbcTemplate.query(sql, employeeRowMapper, department);
    }
    
    @Override
    public void update(Employee employee) {
        String sql = "UPDATE employees SET first_name = ?, last_name = ?, email = ?, " +
                    "salary = ?, department = ? WHERE id = ?";
        
        int rowsAffected = jdbcTemplate.update(sql,
            employee.getFirstName(),
            employee.getLastName(),
            employee.getEmail(),
            employee.getSalary(),
            employee.getDepartment(),
            employee.getId()
        );
        
        if (rowsAffected == 0) {
            throw new EntityNotFoundException("Employee not found with id: " + employee.getId());
        }
    }
    
    @Override
    public void delete(Long id) {
        String sql = "DELETE FROM employees WHERE id = ?";
        int rowsAffected = jdbcTemplate.update(sql, id);
        
        if (rowsAffected == 0) {
            throw new EntityNotFoundException("Employee not found with id: " + id);
        }
    }
    
    @Override
    public List<Employee> findBySalaryRange(Double minSalary, Double maxSalary) {
        String sql = "SELECT * FROM employees WHERE salary BETWEEN ? AND ? ORDER BY salary DESC";
        return jdbcTemplate.query(sql, employeeRowMapper, minSalary, maxSalary);
    }
    
    // Batch operations
    public void saveAll(List<Employee> employees) {
        String sql = "INSERT INTO employees (first_name, last_name, email, salary, department) " +
                    "VALUES (?, ?, ?, ?, ?)";
        
        List<Object[]> batchArgs = employees.stream()
            .map(emp -> new Object[]{
                emp.getFirstName(),
                emp.getLastName(),
                emp.getEmail(),
                emp.getSalary(),
                emp.getDepartment()
            })
            .collect(Collectors.toList());
        
        jdbcTemplate.batchUpdate(sql, batchArgs);
    }
}
```

#### Service layer using DAO:
```java
@Service
@Transactional
public class EmployeeService {
    
    @Autowired
    private EmployeeDAO employeeDAO;
    
    @Autowired
    private DepartmentDAO departmentDAO;
    
    public Employee createEmployee(EmployeeDTO employeeDTO) {
        // Business logic validation
        validateEmployeeData(employeeDTO);
        
        // Check if department exists
        if (!departmentDAO.exists(employeeDTO.getDepartment())) {
            throw new BusinessException("Department does not exist: " + employeeDTO.getDepartment());
        }
        
        // Convert DTO to Entity
        Employee employee = convertToEntity(employeeDTO);
        
        // Save employee
        employeeDAO.save(employee);
        
        // Additional business logic
        updateDepartmentStatistics(employee.getDepartment());
        
        return employee;
    }
    
    @Transactional(readOnly = true)
    public List<Employee> getEmployeesByDepartment(String department) {
        return employeeDAO.findByDepartment(department);
    }
    
    public Employee updateEmployeeSalary(Long employeeId, Double newSalary) {
        Employee employee = employeeDAO.findById(employeeId);
        if (employee == null) {
            throw new EntityNotFoundException("Employee not found");
        }
        
        // Business rules
        if (newSalary < 0) {
            throw new BusinessException("Salary cannot be negative");
        }
        
        String oldDepartment = employee.getDepartment();
        Double oldSalary = employee.getSalary();
        
        employee.setSalary(newSalary);
        employeeDAO.update(employee);
        
        // Update statistics for affected department
        updateDepartmentStatistics(oldDepartment);
        
        // Audit log
        logSalaryChange(employeeId, oldSalary, newSalary);
        
        return employee;
    }
    
    public void transferEmployee(Long employeeId, String newDepartment) {
        Employee employee = employeeDAO.findById(employeeId);
        if (employee == null) {
            throw new EntityNotFoundException("Employee not found");
        }
        
        if (!departmentDAO.exists(newDepartment)) {
            throw new BusinessException("Target department does not exist");
        }
        
        String oldDepartment = employee.getDepartment();
        employee.setDepartment(newDepartment);
        
        employeeDAO.update(employee);
        
        // Update statistics for both departments
        updateDepartmentStatistics(oldDepartment);
        updateDepartmentStatistics(newDepartment);
    }
    
    private void validateEmployeeData(EmployeeDTO dto) {
        if (dto.getEmail() == null || !dto.getEmail().contains("@")) {
            throw new ValidationException("Invalid email address");
        }
        
        if (dto.getSalary() != null && dto.getSalary() < 0) {
            throw new ValidationException("Salary cannot be negative");
        }
    }
    
    private void updateDepartmentStatistics(String department) {
        // Update department statistics in separate service
        // This could be async or event-driven
    }
    
    private void logSalaryChange(Long employeeId, Double oldSalary, Double newSalary) {
        // Audit logging logic
    }
}
```

### 2. **Repository Pattern**

#### C# Entity Framework implementation:
```csharp
// Generic repository interface
public interface IRepository<T> where T : class
{
    Task<T> GetByIdAsync(int id);
    Task<IEnumerable<T>> GetAllAsync();
    Task<IEnumerable<T>> FindAsync(Expression<Func<T, bool>> predicate);
    Task<T> AddAsync(T entity);
    Task UpdateAsync(T entity);
    Task DeleteAsync(int id);
    Task<bool> ExistsAsync(int id);
}

// Specific repository interface
public interface IEmployeeRepository : IRepository<Employee>
{
    Task<IEnumerable<Employee>> GetByDepartmentAsync(string department);
    Task<IEnumerable<Employee>> GetBySalaryRangeAsync(decimal minSalary, decimal maxSalary);
    Task<Employee> GetByEmailAsync(string email);
    Task<IEnumerable<Employee>> GetHighestEarnersAsync(int count);
    Task<decimal> GetAverageSalaryByDepartmentAsync(string department);
}

// Implementation
public class EmployeeRepository : IEmployeeRepository
{
    private readonly CompanyDbContext _context;
    private readonly ILogger<EmployeeRepository> _logger;
    
    public EmployeeRepository(CompanyDbContext context, ILogger<EmployeeRepository> logger)
    {
        _context = context;
        _logger = logger;
    }
    
    public async Task<Employee> GetByIdAsync(int id)
    {
        return await _context.Employees
            .Include(e => e.Department)
            .FirstOrDefaultAsync(e => e.Id == id);
    }
    
    public async Task<IEnumerable<Employee>> GetAllAsync()
    {
        return await _context.Employees
            .Include(e => e.Department)
            .OrderBy(e => e.LastName)
            .ThenBy(e => e.FirstName)
            .ToListAsync();
    }
    
    public async Task<IEnumerable<Employee>> FindAsync(Expression<Func<Employee, bool>> predicate)
    {
        return await _context.Employees
            .Include(e => e.Department)
            .Where(predicate)
            .ToListAsync();
    }
    
    public async Task<Employee> AddAsync(Employee employee)
    {
        _context.Employees.Add(employee);
        await _context.SaveChangesAsync();
        return employee;
    }
    
    public async Task UpdateAsync(Employee employee)
    {
        _context.Employees.Update(employee);
        await _context.SaveChangesAsync();
    }
    
    public async Task DeleteAsync(int id)
    {
        var employee = await GetByIdAsync(id);
        if (employee != null)
        {
            _context.Employees.Remove(employee);
            await _context.SaveChangesAsync();
        }
    }
    
    public async Task<bool> ExistsAsync(int id)
    {
        return await _context.Employees.AnyAsync(e => e.Id == id);
    }
    
    public async Task<IEnumerable<Employee>> GetByDepartmentAsync(string department)
    {
        return await _context.Employees
            .Include(e => e.Department)
            .Where(e => e.Department.Name == department)
            .OrderByDescending(e => e.Salary)
            .ToListAsync();
    }
    
    public async Task<IEnumerable<Employee>> GetBySalaryRangeAsync(decimal minSalary, decimal maxSalary)
    {
        return await _context.Employees
            .Include(e => e.Department)
            .Where(e => e.Salary >= minSalary && e.Salary <= maxSalary)
            .OrderByDescending(e => e.Salary)
            .ToListAsync();
    }
    
    public async Task<Employee> GetByEmailAsync(string email)
    {
        return await _context.Employees
            .Include(e => e.Department)
            .FirstOrDefaultAsync(e => e.Email == email);
    }
    
    public async Task<IEnumerable<Employee>> GetHighestEarnersAsync(int count)
    {
        return await _context.Employees
            .Include(e => e.Department)
            .OrderByDescending(e => e.Salary)
            .Take(count)
            .ToListAsync();
    }
    
    public async Task<decimal> GetAverageSalaryByDepartmentAsync(string department)
    {
        return await _context.Employees
            .Where(e => e.Department.Name == department)
            .AverageAsync(e => e.Salary);
    }
}

// Service using repository
[ApiController]
[Route("api/[controller]")]
public class EmployeesController : ControllerBase
{
    private readonly IEmployeeRepository _employeeRepository;
    private readonly IDepartmentRepository _departmentRepository;
    private readonly IMapper _mapper;
    private readonly ILogger<EmployeesController> _logger;
    
    public EmployeesController(
        IEmployeeRepository employeeRepository,
        IDepartmentRepository departmentRepository,
        IMapper mapper,
        ILogger<EmployeesController> logger)
    {
        _employeeRepository = employeeRepository;
        _departmentRepository = departmentRepository;
        _mapper = mapper;
        _logger = logger;
    }
    
    [HttpGet]
    public async Task<ActionResult<IEnumerable<EmployeeDto>>> GetEmployees(
        [FromQuery] string department = null,
        [FromQuery] decimal? minSalary = null,
        [FromQuery] decimal? maxSalary = null)
    {
        try
        {
            IEnumerable<Employee> employees;
            
            if (!string.IsNullOrEmpty(department))
            {
                employees = await _employeeRepository.GetByDepartmentAsync(department);
            }
            else if (minSalary.HasValue && maxSalary.HasValue)
            {
                employees = await _employeeRepository.GetBySalaryRangeAsync(minSalary.Value, maxSalary.Value);
            }
            else
            {
                employees = await _employeeRepository.GetAllAsync();
            }
            
            var employeeDtos = _mapper.Map<IEnumerable<EmployeeDto>>(employees);
            return Ok(employeeDtos);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving employees");
            return StatusCode(500, "Internal server error");
        }
    }
    
    [HttpPost]
    public async Task<ActionResult<EmployeeDto>> CreateEmployee(CreateEmployeeDto createEmployeeDto)
    {
        try
        {
            // Validate department exists
            var departmentExists = await _departmentRepository.ExistsAsync(createEmployeeDto.DepartmentId);
            if (!departmentExists)
            {
                return BadRequest("Department does not exist");
            }
            
            // Check email uniqueness
            var existingEmployee = await _employeeRepository.GetByEmailAsync(createEmployeeDto.Email);
            if (existingEmployee != null)
            {
                return Conflict("Employee with this email already exists");
            }
            
            var employee = _mapper.Map<Employee>(createEmployeeDto);
            employee.HireDate = DateTime.UtcNow;
            
            var createdEmployee = await _employeeRepository.AddAsync(employee);
            var employeeDto = _mapper.Map<EmployeeDto>(createdEmployee);
            
            return CreatedAtAction(nameof(GetEmployee), new { id = createdEmployee.Id }, employeeDto);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating employee");
            return StatusCode(500, "Internal server error");
        }
    }
    
    [HttpGet("{id}")]
    public async Task<ActionResult<EmployeeDto>> GetEmployee(int id)
    {
        try
        {
            var employee = await _employeeRepository.GetByIdAsync(id);
            if (employee == null)
            {
                return NotFound();
            }
            
            var employeeDto = _mapper.Map<EmployeeDto>(employee);
            return Ok(employeeDto);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving employee {EmployeeId}", id);
            return StatusCode(500, "Internal server error");
        }
    }
}
```

### 3. **Active Record Pattern**

#### Ruby on Rails implementation:
```ruby
# Employee model with Active Record
class Employee < ApplicationRecord
  belongs_to :department
  has_many :salary_histories, dependent: :destroy
  
  validates :first_name, presence: true, length: { minimum: 2, maximum: 50 }
  validates :last_name, presence: true, length: { minimum: 2, maximum: 50 }
  validates :email, presence: true, uniqueness: true, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :salary, presence: true, numericality: { greater_than: 0 }
  
  scope :by_department, ->(dept_name) { joins(:department).where(departments: { name: dept_name }) }
  scope :by_salary_range, ->(min, max) { where(salary: min..max) }
  scope :highest_earners, ->(limit) { order(salary: :desc).limit(limit) }
  scope :recently_hired, -> { where('hire_date > ?', 3.months.ago) }
  
  before_save :normalize_email
  after_update :log_salary_change, if: :saved_change_to_salary?
  
  def full_name
    "#{first_name} #{last_name}"
  end
  
  def senior_employee?
    hire_date < 5.years.ago
  end
  
  def give_raise(amount)
    old_salary = salary
    update!(salary: salary + amount)
    
    SalaryHistory.create!(
      employee: self,
      old_salary: old_salary,
      new_salary: salary,
      change_date: Time.current,
      change_type: 'raise'
    )
  end
  
  def transfer_to_department(new_department)
    transaction do
      old_department = department
      update!(department: new_department)
      
      # Update department statistics
      old_department.update_employee_statistics!
      new_department.update_employee_statistics!
      
      # Log transfer
      Rails.logger.info "Employee #{id} transferred from #{old_department.name} to #{new_department.name}"
    end
  end
  
  # Class methods
  def self.average_salary_by_department
    joins(:department)
      .group('departments.name')
      .average(:salary)
  end
  
  def self.department_statistics
    joins(:department)
      .group('departments.name')
      .select(
        'departments.name as department_name',
        'COUNT(employees.id) as employee_count',
        'AVG(employees.salary) as average_salary',
        'MIN(employees.salary) as min_salary',
        'MAX(employees.salary) as max_salary'
      )
  end
  
  def self.search(query)
    where(
      "first_name ILIKE ? OR last_name ILIKE ? OR email ILIKE ?",
      "%#{query}%", "%#{query}%", "%#{query}%"
    )
  end
  
  private
  
  def normalize_email
    self.email = email.downcase.strip if email.present?
  end
  
  def log_salary_change
    Rails.logger.info "Salary changed for employee #{id}: #{salary_before_last_save} -> #{salary}"
  end
end

# Department model
class Department < ApplicationRecord
  has_many :employees, dependent: :destroy
  
  validates :name, presence: true, uniqueness: true
  validates :budget, numericality: { greater_than: 0 }, allow_nil: true
  
  def employee_count
    employees.count
  end
  
  def average_salary
    employees.average(:salary) || 0
  end
  
  def total_salary_cost
    employees.sum(:salary)
  end
  
  def update_employee_statistics!
    update!(
      employee_count: employees.count,
      average_salary: employees.average(:salary) || 0,
      total_salary_cost: employees.sum(:salary)
    )
  end
  
  def can_hire_employee?(salary)
    budget.nil? || (total_salary_cost + salary) <= budget
  end
end

# Controller using Active Record
class EmployeesController < ApplicationController
  before_action :set_employee, only: [:show, :update, :destroy]
  
  def index
    @employees = Employee.includes(:department)
    
    # Apply filters
    @employees = @employees.by_department(params[:department]) if params[:department].present?
    @employees = @employees.by_salary_range(params[:min_salary], params[:max_salary]) if params[:min_salary] && params[:max_salary]
    @employees = @employees.search(params[:search]) if params[:search].present?
    
    # Pagination
    @employees = @employees.page(params[:page]).per(params[:per_page] || 20)
    
    render json: {
      employees: @employees.as_json(include: :department),
      meta: {
        current_page: @employees.current_page,
        total_pages: @employees.total_pages,
        total_count: @employees.total_count
      }
    }
  end
  
  def show
    render json: @employee.as_json(include: [:department, :salary_histories])
  end
  
  def create
    @employee = Employee.new(employee_params)
    
    if @employee.save
      render json: @employee.as_json(include: :department), status: :created
    else
      render json: { errors: @employee.errors.full_messages }, status: :unprocessable_entity
    end
  end
  
  def update
    if @employee.update(employee_params)
      render json: @employee.as_json(include: :department)
    else
      render json: { errors: @employee.errors.full_messages }, status: :unprocessable_entity
    end
  end
  
  def destroy
    @employee.destroy
    head :no_content
  end
  
  def give_raise
    @employee = Employee.find(params[:id])
    raise_amount = params[:amount].to_f
    
    if raise_amount <= 0
      render json: { error: 'Raise amount must be positive' }, status: :bad_request
      return
    end
    
    @employee.give_raise(raise_amount)
    render json: @employee.as_json(include: :department)
  rescue StandardError => e
    render json: { error: e.message }, status: :unprocessable_entity
  end
  
  def transfer
    @employee = Employee.find(params[:id])
    new_department = Department.find(params[:department_id])
    
    @employee.transfer_to_department(new_department)
    render json: @employee.as_json(include: :department)
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Department not found' }, status: :not_found
  rescue StandardError => e
    render json: { error: e.message }, status: :unprocessable_entity
  end
  
  private
  
  def set_employee
    @employee = Employee.find(params[:id])
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Employee not found' }, status: :not_found
  end
  
  def employee_params
    params.require(:employee).permit(:first_name, :last_name, :email, :salary, :department_id)
  end
end
```

## Wzorce zarządzania transakcjami

### 1. **Programmatic Transaction Management**

#### Spring Framework:
```java
@Service
public class EmployeeService {
    
    @Autowired
    private PlatformTransactionManager transactionManager;
    
    @Autowired
    private EmployeeDAO employeeDAO;
    
    @Autowired
    private DepartmentDAO departmentDAO;
    
    @Autowired
    private AuditLogDAO auditLogDAO;
    
    public void transferEmployeesWithProgrammaticTransaction(
            List<Long> employeeIds, 
            String targetDepartment) {
        
        TransactionDefinition def = new DefaultTransactionDefinition();
        TransactionStatus status = transactionManager.getTransaction(def);
        
        try {
            // Validate target department exists
            Department department = departmentDAO.findByName(targetDepartment);
            if (department == null) {
                throw new BusinessException("Target department does not exist");
            }
            
            List<Employee> transferredEmployees = new ArrayList<>();
            
            for (Long employeeId : employeeIds) {
                Employee employee = employeeDAO.findById(employeeId);
                if (employee == null) {
                    throw new BusinessException("Employee not found: " + employeeId);
                }
                
                String oldDepartment = employee.getDepartment();
                employee.setDepartment(targetDepartment);
                
                employeeDAO.update(employee);
                transferredEmployees.add(employee);
                
                // Create audit log entry
                AuditLog auditLog = new AuditLog();
                auditLog.setEmployeeId(employeeId);
                auditLog.setAction("DEPARTMENT_TRANSFER");
                auditLog.setOldValue(oldDepartment);
                auditLog.setNewValue(targetDepartment);
                auditLog.setTimestamp(LocalDateTime.now());
                
                auditLogDAO.save(auditLog);
            }
            
            // Update department statistics
            Set<String> affectedDepartments = transferredEmployees.stream()
                .map(Employee::getDepartment)
                .collect(Collectors.toSet());
            
            affectedDepartments.add(targetDepartment);
            
            for (String deptName : affectedDepartments) {
                updateDepartmentStatistics(deptName);
            }
            
            transactionManager.commit(status);
            
            // Send notifications (outside transaction)
            notifyDepartmentManagers(affectedDepartments, transferredEmployees);
            
        } catch (Exception e) {
            transactionManager.rollback(status);
            throw e;
        }
    }
    
    private void updateDepartmentStatistics(String departmentName) {
        // Update statistics logic
        Department dept = departmentDAO.findByName(departmentName);
        List<Employee> employees = employeeDAO.findByDepartment(departmentName);
        
        dept.setEmployeeCount(employees.size());
        dept.setAverageSalary(employees.stream()
            .mapToDouble(Employee::getSalary)
            .average()
            .orElse(0.0));
        dept.setTotalSalaryCost(employees.stream()
            .mapToDouble(Employee::getSalary)
            .sum());
        
        departmentDAO.update(dept);
    }
    
    private void notifyDepartmentManagers(Set<String> departments, List<Employee> employees) {
        // Notification logic (async, outside transaction)
        CompletableFuture.runAsync(() -> {
            // Send emails, push notifications, etc.
        });
    }
}
```

### 2. **Declarative Transaction Management**

#### Spring @Transactional:
```java
@Service
@Transactional
public class PayrollService {
    
    @Autowired
    private EmployeeDAO employeeDAO;
    
    @Autowired
    private PayrollDAO payrollDAO;
    
    @Autowired
    private BankingService bankingService;
    
    @Transactional(rollbackFor = Exception.class, timeout = 30)
    public PayrollSummary processPayroll(String department, LocalDate payPeriod) {
        List<Employee> employees = employeeDAO.findByDepartment(department);
        
        PayrollSummary summary = new PayrollSummary();
        summary.setDepartment(department);
        summary.setPayPeriod(payPeriod);
        summary.setProcessedDate(LocalDateTime.now());
        
        List<PayrollEntry> entries = new ArrayList<>();
        
        for (Employee employee : employees) {
            PayrollEntry entry = calculatePayrollEntry(employee, payPeriod);
            
            // Save payroll entry
            payrollDAO.save(entry);
            
            // Process payment (could fail and trigger rollback)
            PaymentResult paymentResult = bankingService.processPayment(
                employee.getBankAccount(),
                entry.getNetPay(),
                "Salary payment for " + payPeriod
            );
            
            entry.setPaymentReference(paymentResult.getTransactionId());
            entry.setPaymentStatus(paymentResult.getStatus());
            
            payrollDAO.update(entry);
            entries.add(entry);
            
            summary.addToTotalGrossPay(entry.getGrossPay());
            summary.addToTotalNetPay(entry.getNetPay());
            summary.addToTotalTaxes(entry.getTotalTax());
        }
        
        summary.setEntries(entries);
        summary.setEmployeeCount(employees.size());
        
        // Save summary
        payrollDAO.saveSummary(summary);
        
        return summary;
    }
    
    @Transactional(readOnly = true)
    public PayrollReport generatePayrollReport(String department, int year) {
        // Read-only transaction for reporting
        List<PayrollSummary> summaries = payrollDAO.findByDepartmentAndYear(department, year);
        
        PayrollReport report = new PayrollReport();
        report.setDepartment(department);
        report.setYear(year);
        
        // Complex calculations...
        calculateYearlyTotals(report, summaries);
        calculateMonthlyAverages(report, summaries);
        calculateTaxBreakdown(report, summaries);
        
        return report;
    }
    
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logPayrollError(Long employeeId, String error, Exception exception) {
        // Always runs in new transaction, even if parent transaction fails
        PayrollErrorLog errorLog = new PayrollErrorLog();
        errorLog.setEmployeeId(employeeId);
        errorLog.setError(error);
        errorLog.setStackTrace(getStackTrace(exception));
        errorLog.setTimestamp(LocalDateTime.now());
        
        payrollDAO.saveErrorLog(errorLog);
    }
    
    @Transactional(propagation = Propagation.NOT_SUPPORTED)
    public void sendPayrollNotifications(PayrollSummary summary) {
        // Runs outside any transaction
        // Won't be affected by transaction rollbacks
        
        for (PayrollEntry entry : summary.getEntries()) {
            try {
                emailService.sendPayslip(entry.getEmployee(), entry);
            } catch (Exception e) {
                // Log error but don't affect main transaction
                logger.error("Failed to send payslip to employee " + entry.getEmployeeId(), e);
            }
        }
    }
    
    private PayrollEntry calculatePayrollEntry(Employee employee, LocalDate payPeriod) {
        PayrollEntry entry = new PayrollEntry();
        entry.setEmployee(employee);
        entry.setPayPeriod(payPeriod);
        
        // Calculate gross pay
        double grossPay = calculateGrossPay(employee);
        entry.setGrossPay(grossPay);
        
        // Calculate deductions
        double incomeTax = calculateIncomeTax(grossPay);
        double socialSecurity = calculateSocialSecurity(grossPay);
        double healthInsurance = calculateHealthInsurance(employee);
        
        entry.setIncomeTax(incomeTax);
        entry.setSocialSecurity(socialSecurity);
        entry.setHealthInsurance(healthInsurance);
        
        // Calculate net pay
        double totalDeductions = incomeTax + socialSecurity + healthInsurance;
        entry.setNetPay(grossPay - totalDeductions);
        
        return entry;
    }
}
```

### 3. **Database Transaction Patterns**

#### Unit of Work Pattern:
```python
class UnitOfWork:
    def __init__(self, connection_factory):
        self.connection_factory = connection_factory
        self._connection = None
        self._transaction = None
        self._repositories = {}
    
    def __enter__(self):
        self._connection = self.connection_factory.create_connection()
        self._transaction = self._connection.begin()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        
        if self._connection:
            self._connection.close()
    
    def commit(self):
        if self._transaction:
            self._transaction.commit()
    
    def rollback(self):
        if self._transaction:
            self._transaction.rollback()
    
    def get_repository(self, repository_class):
        if repository_class not in self._repositories:
            self._repositories[repository_class] = repository_class(self._connection)
        return self._repositories[repository_class]

class EmployeeService:
    def __init__(self, unit_of_work_factory):
        self.uow_factory = unit_of_work_factory
    
    def transfer_employees_between_departments(self, employee_ids, source_dept, target_dept):
        with self.uow_factory() as uow:
            employee_repo = uow.get_repository(EmployeeRepository)
            department_repo = uow.get_repository(DepartmentRepository)
            audit_repo = uow.get_repository(AuditRepository)
            
            # Validate departments exist
            source_department = department_repo.get_by_name(source_dept)
            target_department = department_repo.get_by_name(target_dept)
            
            if not source_department or not target_department:
                raise ValueError("Invalid department")
            
            # Check target department capacity
            if not target_department.can_accommodate_employees(len(employee_ids)):
                raise BusinessError("Target department at capacity")
            
            transferred_employees = []
            
            for employee_id in employee_ids:
                employee = employee_repo.get_by_id(employee_id)
                if not employee or employee.department_id != source_department.id:
                    raise ValueError(f"Employee {employee_id} not in source department")
                
                # Update employee
                employee.department_id = target_department.id
                employee.transfer_date = datetime.now()
                employee_repo.update(employee)
                
                transferred_employees.append(employee)
                
                # Create audit record
                audit_record = AuditRecord(
                    employee_id=employee_id,
                    action='DEPARTMENT_TRANSFER',
                    old_value=source_dept,
                    new_value=target_dept,
                    timestamp=datetime.now()
                )
                audit_repo.add(audit_record)
            
            # Update department statistics
            source_department.employee_count -= len(employee_ids)
            target_department.employee_count += len(employee_ids)
            
            department_repo.update(source_department)
            department_repo.update(target_department)
            
            # Unit of Work will commit all changes together
            return transferred_employees

# Usage
def transfer_it_employees_to_engineering():
    uow_factory = UnitOfWorkFactory(database_config)
    employee_service = EmployeeService(uow_factory)
    
    try:
        employee_ids = [101, 102, 103, 104]
        transferred = employee_service.transfer_employees_between_departments(
            employee_ids, 'IT', 'Engineering'
        )
        
        print(f"Successfully transferred {len(transferred)} employees")
        
        # Send notifications outside the transaction
        for employee in transferred:
            notification_service.send_transfer_notification(employee)
            
    except Exception as e:
        print(f"Transfer failed: {e}")
        # All database changes will be rolled back automatically
```

## Connection Pooling i zarządzanie zasobami

### 1. **HikariCP (Java)**

```java
@Configuration
public class DatabaseConfig {
    
    @Bean
    @Primary
    @ConfigurationProperties("app.datasource.main")
    public DataSourceProperties mainDataSourceProperties() {
        return new DataSourceProperties();
    }
    
    @Bean
    @Primary
    public DataSource mainDataSource() {
        HikariConfig config = new HikariConfig();
        
        // Basic connection settings
        config.setJdbcUrl("jdbc:postgresql://localhost:5432/company_db");
        config.setUsername("app_user");
        config.setPassword("app_password");
        config.setDriverClassName("org.postgresql.Driver");
        
        // Pool settings
        config.setMaximumPoolSize(20);              // Maximum number of connections
        config.setMinimumIdle(5);                   // Minimum idle connections
        config.setConnectionTimeout(30000);         // 30 seconds
        config.setIdleTimeout(600000);              // 10 minutes
        config.setMaxLifetime(1800000);             // 30 minutes
        config.setLeakDetectionThreshold(60000);    // 1 minute
        
        // Performance settings
        config.setConnectionTestQuery("SELECT 1");
        config.setValidationTimeout(5000);
        config.setInitializationFailTimeout(1);
        
        // Connection properties
        config.addDataSourceProperty("cachePrepStmts", "true");
        config.addDataSourceProperty("prepStmtCacheSize", "250");
        config.addDataSourceProperty("prepStmtCacheSqlLimit", "2048");
        config.addDataSourceProperty("useServerPrepStmts", "true");
        config.addDataSourceProperty("useLocalSessionState", "true");
        config.addDataSourceProperty("rewriteBatchedStatements", "true");
        config.addDataSourceProperty("cacheResultSetMetadata", "true");
        config.addDataSourceProperty("cacheServerConfiguration", "true");
        config.addDataSourceProperty("elideSetAutoCommits", "true");
        config.addDataSourceProperty("maintainTimeStats", "false");
        
        return new HikariDataSource(config);
    }
    
    @Bean
    @ConfigurationProperties("app.datasource.readonly")
    public DataSourceProperties readOnlyDataSourceProperties() {
        return new DataSourceProperties();
    }
    
    @Bean
    public DataSource readOnlyDataSource() {
        // Separate read-only connection pool for reporting queries
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:postgresql://readonly-replica:5432/company_db");
        config.setUsername("readonly_user");
        config.setPassword("readonly_password");
        config.setMaximumPoolSize(10);
        config.setReadOnly(true);
        
        return new HikariDataSource(config);
    }
    
    @Bean
    public JdbcTemplate jdbcTemplate(@Qualifier("mainDataSource") DataSource dataSource) {
        return new JdbcTemplate(dataSource);
    }
    
    @Bean
    public JdbcTemplate readOnlyJdbcTemplate(@Qualifier("readOnlyDataSource") DataSource dataSource) {
        return new JdbcTemplate(dataSource);
    }
}

// Service using different data sources
@Service
public class EmployeeAnalyticsService {
    
    @Autowired
    @Qualifier("readOnlyJdbcTemplate")
    private JdbcTemplate readOnlyJdbcTemplate;
    
    @Autowired
    @Qualifier("jdbcTemplate")
    private JdbcTemplate mainJdbcTemplate;
    
    public List<DepartmentStats> getDepartmentStatistics() {
        // Use read-only replica for reporting queries
        String sql = """
            SELECT 
                d.name as department_name,
                COUNT(e.id) as employee_count,
                AVG(e.salary) as average_salary,
                MIN(e.salary) as min_salary,
                MAX(e.salary) as max_salary,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY e.salary) as median_salary
            FROM departments d
            LEFT JOIN employees e ON d.id = e.department_id
            GROUP BY d.id, d.name
            ORDER BY average_salary DESC
        """;
        
        return readOnlyJdbcTemplate.query(sql, (rs, rowNum) -> {
            DepartmentStats stats = new DepartmentStats();
            stats.setDepartmentName(rs.getString("department_name"));
            stats.setEmployeeCount(rs.getInt("employee_count"));
            stats.setAverageSalary(rs.getDouble("average_salary"));
            stats.setMinSalary(rs.getDouble("min_salary"));
            stats.setMaxSalary(rs.getDouble("max_salary"));
            stats.setMedianSalary(rs.getDouble("median_salary"));
            return stats;
        });
    }
    
    public void updateEmployeeSalary(Long employeeId, Double newSalary) {
        // Use main data source for write operations
        String sql = "UPDATE employees SET salary = ? WHERE id = ?";
        mainJdbcTemplate.update(sql, newSalary, employeeId);
    }
}
```

### 2. **Connection Pool Monitoring**

```java
@Component
public class DatabaseHealthIndicator implements HealthIndicator {
    
    @Autowired
    private DataSource dataSource;
    
    @Override
    public Health health() {
        try {
            if (dataSource instanceof HikariDataSource) {
                HikariDataSource hikariDataSource = (HikariDataSource) dataSource;
                HikariPoolMXBean poolBean = hikariDataSource.getHikariPoolMXBean();
                
                Health.Builder builder = Health.up()
                    .withDetail("database", "PostgreSQL")
                    .withDetail("activeConnections", poolBean.getActiveConnections())
                    .withDetail("idleConnections", poolBean.getIdleConnections())
                    .withDetail("totalConnections", poolBean.getTotalConnections())
                    .withDetail("threadsAwaitingConnections", poolBean.getThreadsAwaitingConnection());
                
                // Check if pool is healthy
                if (poolBean.getActiveConnections() >= poolBean.getMaximumPoolSize() * 0.9) {
                    builder.status("WARN")
                           .withDetail("warning", "Connection pool nearly exhausted");
                }
                
                return builder.build();
            } else {
                return Health.up()
                    .withDetail("database", "Connected")
                    .build();
            }
        } catch (Exception e) {
            return Health.down()
                .withDetail("database", "Connection failed")
                .withException(e)
                .build();
        }
    }
}

@RestController
@RequestMapping("/admin")
public class DatabaseAdminController {
    
    @Autowired
    private DataSource dataSource;
    
    @GetMapping("/db-metrics")
    public ResponseEntity<Map<String, Object>> getDatabaseMetrics() {
        Map<String, Object> metrics = new HashMap<>();
        
        if (dataSource instanceof HikariDataSource) {
            HikariDataSource hikariDataSource = (HikariDataSource) dataSource;
            HikariPoolMXBean poolBean = hikariDataSource.getHikariPoolMXBean();
            
            metrics.put("activeConnections", poolBean.getActiveConnections());
            metrics.put("idleConnections", poolBean.getIdleConnections());
            metrics.put("totalConnections", poolBean.getTotalConnections());
            metrics.put("threadsAwaitingConnections", poolBean.getThreadsAwaitingConnection());
            metrics.put("maximumPoolSize", poolBean.getMaximumPoolSize());
            metrics.put("minimumIdle", poolBean.getMinimumIdle());
        }
        
        return ResponseEntity.ok(metrics);
    }
    
    @PostMapping("/db-pool/soft-evict")
    public ResponseEntity<String> softEvictConnections() {
        if (dataSource instanceof HikariDataSource) {
            HikariDataSource hikariDataSource = (HikariDataSource) dataSource;
            HikariPoolMXBean poolBean = hikariDataSource.getHikariPoolMXBean();
            
            poolBean.softEvictConnections();
            return ResponseEntity.ok("Connections soft evicted");
        }
        
        return ResponseEntity.badRequest().body("Not a HikariCP pool");
    }
}
```

## Error Handling i Resilience

### 1. **Retry Mechanisms**

```java
@Component
public class DatabaseRetryService {
    
    private static final Logger logger = LoggerFactory.getLogger(DatabaseRetryService.class);
    
    @Retryable(
        value = {SQLException.class, DataAccessException.class},
        maxAttempts = 3,
        backoff = @Backoff(delay = 1000, multiplier = 2)
    )
    public Employee saveEmployeeWithRetry(Employee employee) {
        try {
            return employeeRepository.save(employee);
        } catch (DataAccessException e) {
            logger.warn("Database operation failed, retrying... Attempt: {}", 
                getCurrentAttempt(), e);
            throw e; // Re-throw to trigger retry
        }
    }
    
    @Recover
    public Employee recoverSaveEmployee(DataAccessException ex, Employee employee) {
        logger.error("Failed to save employee after all retry attempts", ex);
        
        // Alternative actions:
        // 1. Save to message queue for later processing
        // 2. Write to file system
        // 3. Send to dead letter queue
        
        throw new BusinessException("Unable to save employee, please try again later", ex);
    }
    
    // Circuit breaker pattern
    @CircuitBreaker(
        name = "database",
        fallbackMethod = "fallbackGetEmployees"
    )
    public List<Employee> getEmployeesWithCircuitBreaker(String department) {
        return employeeRepository.findByDepartment(department);
    }
    
    public List<Employee> fallbackGetEmployees(String department, Exception ex) {
        logger.warn("Circuit breaker activated for getEmployees", ex);
        
        // Return cached data or empty list
        return cacheService.getCachedEmployees(department)
            .orElse(Collections.emptyList());
    }
}
```

### 2. **Graceful Degradation**

```python
import asyncio
import logging
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

class ServiceHealth(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    UNHEALTHY = "unhealthy"

@dataclass
class EmployeeServiceConfig:
    primary_db_timeout: int = 5
    fallback_db_timeout: int = 10
    cache_ttl: int = 300
    max_retries: int = 3

class ResilientEmployeeService:
    def __init__(self, 
                 primary_db: DatabaseConnection,
                 fallback_db: DatabaseConnection,
                 cache_service: CacheService,
                 config: EmployeeServiceConfig):
        self.primary_db = primary_db
        self.fallback_db = fallback_db
        self.cache = cache_service
        self.config = config
        self.health_status = ServiceHealth.HEALTHY
        self.logger = logging.getLogger(__name__)
    
    async def get_employees(self, department: str) -> List[Employee]:
        cache_key = f"employees:{department}"
        
        # Try cache first
        cached_employees = await self.cache.get(cache_key)
        if cached_employees:
            return cached_employees
        
        # Try primary database
        try:
            employees = await self._get_from_primary_db(department)
            if employees:
                await self.cache.set(cache_key, employees, ttl=self.config.cache_ttl)
                self._update_health_status(ServiceHealth.HEALTHY)
                return employees
                
        except DatabaseException as e:
            self.logger.warning(f"Primary database failed: {e}")
            self._update_health_status(ServiceHealth.DEGRADED)
        
        # Fallback to secondary database
        try:
            employees = await self._get_from_fallback_db(department)
            if employees:
                await self.cache.set(cache_key, employees, ttl=self.config.cache_ttl)
                return employees
                
        except DatabaseException as e:
            self.logger.error(f"Fallback database failed: {e}")
            self._update_health_status(ServiceHealth.UNHEALTHY)
        
        # Last resort: return empty list or cached stale data
        stale_data = await self.cache.get_stale(cache_key)
        if stale_data:
            self.logger.info("Returning stale cached data")
            return stale_data
        
        self.logger.error("All data sources failed, returning empty list")
        return []
    
    async def save_employee(self, employee: Employee) -> bool:
        for attempt in range(self.config.max_retries):
            try:
                # Try primary database first
                success = await self._save_to_primary_db(employee)
                if success:
                    # Invalidate cache
                    await self.cache.delete(f"employees:{employee.department}")
                    self._update_health_status(ServiceHealth.HEALTHY)
                    return True
                    
            except DatabaseException as e:
                self.logger.warning(f"Save attempt {attempt + 1} failed: {e}")
                
                if attempt < self.config.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(wait_time)
                else:
                    # Queue for later processing
                    await self._queue_for_retry(employee)
                    self._update_health_status(ServiceHealth.DEGRADED)
                    return False
        
        return False
    
    async def _get_from_primary_db(self, department: str) -> List[Employee]:
        timeout = self.config.primary_db_timeout
        query = "SELECT * FROM employees WHERE department = %s"
        
        async with asyncio.timeout(timeout):
            return await self.primary_db.query(query, [department])
    
    async def _get_from_fallback_db(self, department: str) -> List[Employee]:
        timeout = self.config.fallback_db_timeout
        query = "SELECT * FROM employees WHERE department = %s"
        
        async with asyncio.timeout(timeout):
            return await self.fallback_db.query(query, [department])
    
    async def _save_to_primary_db(self, employee: Employee) -> bool:
        timeout = self.config.primary_db_timeout
        query = """
            INSERT INTO employees (first_name, last_name, email, salary, department)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        async with asyncio.timeout(timeout):
            result = await self.primary_db.execute(query, [
                employee.first_name,
                employee.last_name,
                employee.email,
                employee.salary,
                employee.department
            ])
            return result.rowcount > 0
    
    async def _queue_for_retry(self, employee: Employee):
        # Queue failed operations for later retry
        retry_task = {
            'operation': 'save_employee',
            'data': employee.to_dict(),
            'timestamp': datetime.now().isoformat(),
            'attempts': 0
        }
        
        await self.retry_queue.enqueue(retry_task)
        self.logger.info(f"Queued employee save for retry: {employee.email}")
    
    def _update_health_status(self, status: ServiceHealth):
        if self.health_status != status:
            self.logger.info(f"Service health changed: {self.health_status} -> {status}")
            self.health_status = status
    
    def get_health_status(self) -> dict:
        return {
            'status': self.health_status.value,
            'primary_db': self._check_db_health(self.primary_db),
            'fallback_db': self._check_db_health(self.fallback_db),
            'cache': self._check_cache_health(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _check_db_health(self, db: DatabaseConnection) -> str:
        try:
            # Simple health check query
            result = db.query_sync("SELECT 1", timeout=1)
            return "healthy" if result else "unhealthy"
        except Exception:
            return "unhealthy"
    
    def _check_cache_health(self) -> str:
        try:
            # Ping cache service
            success = self.cache.ping()
            return "healthy" if success else "unhealthy"
        except Exception:
            return "unhealthy"

# Usage with dependency injection
async def main():
    config = EmployeeServiceConfig(
        primary_db_timeout=5,
        fallback_db_timeout=10,
        cache_ttl=300,
        max_retries=3
    )
    
    primary_db = PostgreSQLConnection("primary_host:5432")
    fallback_db = PostgreSQLConnection("fallback_host:5432")
    cache = RedisCache("cache_host:6379")
    
    employee_service = ResilientEmployeeService(
        primary_db, fallback_db, cache, config
    )
    
    # Get employees with automatic fallback
    employees = await employee_service.get_employees("Engineering")
    
    # Check service health
    health = employee_service.get_health_status()
    print(f"Service health: {health}")
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**

#### 1. **Separation of Concerns**
```java
// ✅ Clear layered architecture
@Controller  // Presentation layer
@Service     // Business logic layer  
@Repository  // Data access layer
@Entity      // Domain model

// ✅ Dependency injection
@Autowired
private EmployeeRepository employeeRepository;
```

#### 2. **Transaction Management**
```java
// ✅ Proper transaction boundaries
@Transactional(rollbackFor = Exception.class)
public void businessOperation() {
    // All database operations in single transaction
}

// ✅ Read-only transactions for queries
@Transactional(readOnly = true)
public List<Employee> getEmployees() {
    return employeeRepository.findAll();
}
```

#### 3. **Error Handling**
```java
// ✅ Specific exception handling
try {
    employee = employeeRepository.save(employee);
} catch (DataIntegrityViolationException e) {
    throw new BusinessException("Email already exists");
} catch (DataAccessException e) {
    throw new SystemException("Database error", e);
}
```

### ❌ **Złe praktyki:**

```java
// ❌ Database logic in controller
@GetMapping("/employees")
public List<Employee> getEmployees() {
    String sql = "SELECT * FROM employees";
    return jdbcTemplate.query(sql, rowMapper);  // WRONG!
}

// ❌ No transaction management
public void transferMoney(Account from, Account to, BigDecimal amount) {
    from.withdraw(amount);  // Could fail after this
    to.deposit(amount);     // Leaving inconsistent state
}

// ❌ Ignoring database errors
try {
    repository.save(entity);
} catch (Exception e) {
    // Silently ignoring errors - WRONG!
}

// ❌ Not closing resources
Connection conn = DriverManager.getConnection(url);
// Using connection...
// Not closed - resource leak!
```

## Pułapki egzaminacyjne

### 1. **Transaction Boundaries**
```
@Transactional na metodach publicznych - nie działa na metodach private
Propagation types: REQUIRED, REQUIRES_NEW, SUPPORTS, NOT_SUPPORTED
Rollback tylko dla RuntimeException (domyślnie)
```

### 2. **Connection Pooling**
```
Maksymalna liczba połączeń = max_connections w bazie
Timeout settings: connection, idle, max lifetime
Connection leaks = nie zamknięte połączenia
```

### 3. **DAO vs Repository**
```
DAO - koncentruje się na operacjach na danych
Repository - koncentruje się na kolekcji obiektów domeny
Active Record - obiekty zawierają logikę persistencji
```

### 4. **Exception Handling**
```
Checked vs Unchecked exceptions
DataAccessException hierarchy w Spring
SQLException vs business exceptions
```