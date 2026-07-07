# BudgetApp — Gestión de Presupuestos

Aplicación web en Django para gestionar presupuestos colaborativos con soporte de gastos en efectivo y tarjeta (con cuotas).

## Stack

- **Python 3** + **Django 6.x**
- **SQLite** (base de datos)
- **Bootstrap 5.3** (interfaz responsive, dark mode)
- **Chart.js** (gráficos en reportes)
- **django-crispy-forms** + **crispy-bootstrap5**

## Roles

| Rol | Acciones |
|---|---|
| **Admin** (staff) | Crear usuarios, crear presupuestos, asignar/remover usuarios a presupuestos |
| **Usuario miembro** | Gestionar categorías del presupuesto, registrar gastos, consultar por rango de fechas, ver reportes |

## Modelos de datos

### `User`
- Hereda de `AbstractUser`
- `force_password_change` (bool) — obliga al usuario a cambiar su contraseña en el primer login

### `Budget` (presupuesto/proyecto)
- `name`, `description`, `created_by` (FK → User), `created_at`
- `members` (M2M → User via `BudgetMembership`)

### `BudgetMembership`
- `budget` (FK), `user` (FK), `added_by` (FK), `added_at`

### `Category`
- `name`, `budget` (FK), `created_by` (FK), `created_at`

### `Expense` (gasto)
- `budget` (FK), `category` (FK), `description`, `expense_date`
- `payment_type`: `cash` (efectivo) o `card` (tarjeta)
- `total_amount`, `created_by` (FK), `created_at`

### `ExpenseInstallment` (cuota)
- `expense` (FK), `installment_number`, `amount`
- `effective_month`, `effective_year` — mes y año en que esta cuota impacta

#### Lógica de cuotas
- **Efectivo**: se crea 1 cuota que impacta en el mismo mes del gasto
- **Tarjeta**: se crean N cuotas que impactan en los meses siguientes al del gasto (el usuario indica el monto de cada cuota individualmente)

## Autenticación

1. El **admin** crea usuarios con una contraseña temporal
2. El usuario inicia sesión con esa contraseña temporal
3. El sistema lo redirige automáticamente a cambiar la contraseña
4. Una vez cambiada, accede al dashboard

## Rutas

### Admin (requiere `is_staff`)

| Ruta | Descripción |
|---|---|
| `/admin-panel/` | Panel principal con listado de usuarios y presupuestos |
| `/admin-panel/users/create/` | Crear nuevo usuario |
| `/budgets/` | Listar presupuestos |
| `/budgets/create/` | Crear presupuesto |
| `/budgets/<id>/edit/` | Editar presupuesto |
| `/budgets/<id>/assign/` | Asignar usuario a presupuesto |
| `/budgets/<id>/members/` | Ver/remover miembros del presupuesto |

### Usuario miembro (requiere autenticación y membresía)

| Ruta | Descripción |
|---|---|
| `/dashboard/` | Dashboard principal con resumen de presupuestos del usuario |
| `/budgets/<id>/dashboard/` | Dashboard del presupuesto por mes |
| `/budgets/<id>/categories/` | CRUD de categorías |
| `/budgets/<id>/expenses/` | CRUD de gastos + filtro por rango de fechas |
| `/budgets/<id>/reports/` | Reportes con gráfico de torta y resumen por categoría |

## Inicio rápido

```bash
# 1. Activar el entorno virtual
source venv/bin/activate

# 2. Crear la base de datos (ya ejecutado, pero si empezás de cero)
# python manage.py migrate

# 3. Iniciar servidor
python manage.py runserver

# 4. Abrir en el navegador
# http://localhost:8000
```

### Usuario admin por defecto

- **Usuario:** `admin`
- **Contraseña:** `admin123`

> Cambiar la contraseña del admin en producción.

## Uso básico

1. Iniciar sesión como **admin** → ir al panel de administración
2. Crear usuarios desde el panel
3. Crear un presupuesto (proyecto)
4. Asignar usuarios al presupuesto
5. Cada usuario inicia sesión con su contraseña temporal, la cambia, y accede al presupuesto
6. Dentro del presupuesto: crear categorías, registrar gastos, consultar por fechas, ver reportes

## Desarrollo

Para agregar nuevas dependencias, agregarlas a `requirements.txt` e instalar:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

Para ejecutar migraciones después de cambiar modelos:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Estructura del proyecto

```
budget/
├── config/                    # Configuración del proyecto Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                      # App principal
│   ├── models.py              # User, Budget, Category, Expense, ExpenseInstallment
│   ├── views.py               # Todas las vistas
│   ├── forms.py               # Formularios
│   ├── urls.py                # Rutas
│   ├── admin.py               # Registro en admin de Django
│   └── templates/core/        # Templates HTML con Bootstrap 5
├── manage.py
├── requirements.txt
└── README.md
```
