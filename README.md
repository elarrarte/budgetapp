# BudgetApp — Gestión de Presupuestos

Aplicación web en Django para gestionar presupuestos colaborativos con soporte de gastos en efectivo y tarjeta (con cuotas).

## Stack

- **Python 3** + **Django 6.x**
- **SQLite** (base de datos)
- **Bootstrap 5.3** (interfaz responsive, dark mode)
- **Chart.js** (gráficos en dashboard)
- **django-crispy-forms** + **crispy-bootstrap5**

## Roles

| Rol | Acciones |
|---|---|
| **Admin** (staff) | Crear usuarios, crear presupuestos, asignar/remover usuarios a presupuestos |
| **Usuario miembro** | Gestionar categorías del presupuesto, registrar gastos, ver dashboard con chart y detalle mensual |

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
- `name`, `color` (hex, ej. `#e6194b`), `budget` (FK), `created_by` (FK), `created_at`

### `Expense` (gasto)
- `budget` (FK), `category` (FK), `description`, `expense_date`
- `payment_type`: `cash` (efectivo) o `card` (tarjeta)
- `created_by` (FK), `created_at`

### `ExpenseInstallment` (cuota)
- `expense` (FK), `installment_number`, `amount` (IntegerField)
- `effective_date` — fecha en que esta cuota impacta

#### Lógica de cuotas
- **Efectivo**: se crea 1 cuota que impacta en el mismo mes del gasto
- **Tarjeta**: se crean N cuotas con el mismo monto que impactan en los meses siguientes al del gasto (el usuario indica cantidad de cuotas y monto por cuota)

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
| `/budgets/<id>/dashboard/` | Dashboard del presupuesto con chart, resumen por categoría y detalle de gastos |
| `/budgets/<id>/categories/` | CRUD de categorías (con selector de color) |
| `/budgets/<id>/expenses/` | CRUD de gastos con filtro por mes-año |

## Inicio rápido

```bash
# 1. Activar el entorno virtual
source venv/bin/activate

# 2. Crear la base de datos (ya ejecutado, pero si empezás de cero)
# python manage.py migrate

# 3. Iniciar servidor (accesible desde cualquier dispositivo en la red)
python manage.py runserver 0.0.0.0:8000

# 4. Abrir en el navegador
# http://localhost:8000
```

### Usuario admin por defecto

- **Usuario:** `admin`
- **Contraseña:** `admin123`

> Cambiar la contraseña del admin en producción.

## Funcionalidades

### Navegación
- **Menú único responsive**: navbar con hamburguesa en mobile que agrupa navegación del presupuesto (Dashboard, Categorías, Gastos) y menú de usuario
- **Período persistente**: el mes/año seleccionado se guarda en sesión al navegar entre secciones
- **Flechas ← →**: navegación rápida entre meses sin abrir el selector

### Gestión de gastos
- **Efectivo**: monto único, impacta en el mes de la compra
- **Tarjeta**: cantidad de cuotas + monto por cuota (mismo valor para todas); las cuotas impactan desde el mes siguiente
- **Botón "Hoy"**: setea la fecha actual automáticamente en el formulario
- **Guardar y crear otro**: guarda el gasto actual y abre un formulario limpio para el siguiente

### Dashboard
- Chart.js doughnut con colores de categoría
- Resumen por categoría (monto y porcentaje)
- Detalle de gastos con todas las cuotas del período
- Cards de total, efectivo y tarjeta

### Categorías
- CRUD completo con selector de color (`<input type="color">`)
- Color visible en el chart del dashboard

## Uso básico

1. Iniciar sesión como **admin** → ir al panel de administración
2. Crear usuarios desde el panel
3. Crear un presupuesto (proyecto)
4. Asignar usuarios al presupuesto
5. Cada usuario inicia sesión con su contraseña temporal, la cambia, y accede al presupuesto
6. Dentro del presupuesto: crear categorías (con color), registrar gastos (efectivo/tarjeta), ver dashboard mensual

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

## Instalación completa desde cero

### Prerrequisitos

- **Git** — para clonar el repositorio
- **Python 3.12+** — `python --version` o `python3 --version`
- **python3-venv** — `apt install python3-venv` (Debian/Ubuntu)

### Pasos

```bash
# 1. Clonar el repositorio
git clone git@github.com:elarrarte/budgetapp.git
cd budgetapp

# 2. Crear virtualenv e instalar dependencias
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Migrar base de datos
python manage.py migrate

# 4. Crear superusuario (admin)
python manage.py createsuperuser

# 5. Instalar servicio systemd (ver sección siguiente)
```

> Si `python` no existe en tu sistema, usar `python3`.
> Para recargar cambios del modelo: `python manage.py makemigrations && python manage.py migrate`

## Instalación como servicio systemd (usuario)

> Asegurate de haber completado los pasos 1 a 4 de la sección anterior.

```bash
# Copiar el service unit
cp deploy/budgetapp.service ~/.config/systemd/user/

# Recargar systemd y habilitar
systemctl --user daemon-reload
systemctl --user enable budgetapp.service
systemctl --user start budgetapp.service

# Ver logs
journalctl --user -u budgetapp.service -f
```

### Personalizar sin modificar el service unit

Crear `~/.config/systemd/user/budgetapp.service.d/override.conf`:

```ini
[Service]
# Ejemplo: cambiar puerto
ExecStart=
ExecStart=%h/git/personal/budgetapp/venv/bin/python manage.py runserver 0.0.0.0:8080
```

```bash
mkdir -p ~/.config/systemd/user/budgetapp.service.d/
systemctl --user daemon-reload
systemctl --user restart budgetapp.service
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
│   └── templates/core/        # Templates HTML con Bootstrap 5 (navbar único en base.html)
├── deploy/                    # Archivos de despliegue
│   └── budgetapp.service      # Service unit systemd
├── manage.py
├── requirements.txt
└── README.md
```
