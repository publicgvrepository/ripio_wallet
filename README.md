# django_ripio

Descripción del proyecto

## Requerimientos

- Python
- Django
- DRF
- Docker
- Docker-compose

## Estructura del proyecto

`backend/`
 - `config/` - Contiene las configuraciones relacionadas a todo el proyecto.
 - `requirements/` - Dependencias divididas por ambiente
 - `apps/` - Contendrá las apps de Django del proyecto
 - `VERSION` - Este archivo contiene el número de versión del proyecto. Se deberá actualizar cada vez que se cree una nueva release.

## Instalación


### Setup ambiente de desarrollo con docker-compose

En la raíz del proyecto, para construir imágenes y levantar:
```bash
docker-compose -p RIPIO up --build

```

Una vez corriendo los dockers, en otra terminal en la raíz del proyecto, para hacer la carga de datos iniciales:
```bash
docker exec -it django_ripio python backend/manage.py loaddata backend/apps/users/fixtures/db_data.json
```
Con esto se cargarán (entre otras cosas) algunos usuarios (todos con password 12qwaszx), el usuario admin (password admin).

### Uso

#### ADMIN

Ingresar con user/password = admin/admin a http://localhost:8000/admin


####  API Endpoints

A través de la interfáz gráfica con Swagger, ingresar a http://localhost:8000/swagger/

Registrar un usuario: http://localhost:8000/swagger/#/api/api_users_sing_up_create

Loguear a un usuario (la password de tods es 12qwaszx) (de aquí obtendremos el JWT): http://localhost:8000/swagger/#/api/api_token_create

Consultar las transacciones por usuario (con su JWT): http://localhost:8000/swagger/#/api/api_transactions_retrieve

Conultar balance de las monedas (con su JWT): http://localhost:8000/swagger/#/api/api_wallet_retrieve


### Limitaciones

- Si se agregan más monedas, deberá asociarlas a las wallet de cada usuario ya existente. Para los nuevos se asociará automáticamente con monto 0
- Si quiere agregar dinero en las wallet, deberá hacerlo por admin
- Sólo se pueden hacer transferencias de a una moneda


## Test

Con los contenedores corriendo, en una nueva terminal ejecutar:

```
docker exec -it django_ripio pytest -vvv backend/
```

## Stack tecnológico

- Python [3.8]
- Django [3.2.6 - (3.2 - LTS)]
- Django REST Framework [3.12.4]
- PostgreSQL [Docker - postgres:13-alpine]
- Pytest [6]
