# Proyecto Pasta Loca

## Objetivo del Proyecto

- **Análisis avanzado de insights y cohortes**: Estudio detallado del comportamiento de los usuarios a lo largo del tiempo.
- **Segmentación de datos exhaustiva**: Dividir a los usuarios en grupos con base en el periodo de su primer adelanto.
- **Análisis de cohortes de usuarios relevantes**: Definidas según el primer "created_at" de cada `user_id`.

## Alcance del Proyecto

- Generar modelos de regresión y clasificación para proporcionar a BP valiosas perspectivas sobre el comportamiento de los usuarios y el rendimiento de sus servicios financieros.

## Diagrama de Flujo del Servicio

(Enlace al diagrama de flujo definitivo)

# METRICAS PARA ANALIZAR RENTABILIDAD FINANCIERA DE BP

- Margen de ingreso por fees = (ingresos por fees de adelanto + ingresos por fees de prorrogas) / total adelantos * 100

- Porcentaje de adelantos con fee = adelantos con fee / total adelantos * 100

# METRICAS PARA ANALIZAR COMPORTAMIENTO DE CLIENTES DE BP

- Porcentaje de clientes repetitivos: Clientes repetitivos / Total de Clientes * 100

- Porcentaje de nuevos clientes que pagan fees=  Clientes nuevos que pagan fees / Total de clientes nuevos * 100
  
- Porcentaje de clientes repetitivos que pagan fees=  Clientes repetitivos que pagan fees / Total de clientes repetitivos * 100

- Tasa de incumplimiento nuevos clientes: (Clientes nuevos que no cumplen el plazo / Total de clientes nuevos) * 100

- Tasa de incumplimiento clientes repetitivos: (Clientes repetitivos que no cumplen el plazo / Total de clientes repetitivos) * 100


---

## Estructura de los Datos

### Cash_Request

#### CR Campo: Status (23970 registros)

- **money_back**: 16397 registros. El CR fue reembolsado exitosamente.
- **rejected**: 6568 registros. El CR necesitó una revisión manual y fue rechazado.
- **direct_debit_rejected**: 831 registros. El intento de débito directo SEPA falló.
- **active**: 59 registros. Los fondos fueron recibidos en la cuenta del cliente.
- **transaction_declined**: 48 registros. No se pudo enviar el dinero al cliente.
- **canceled**: 33 registros. El usuario no confirmó el CR en la app, fue cancelado automáticamente.
- **direct_debit_sent**: 34 registros. Se envió un débito directo SEPA, pero aún no se confirma el resultado.

#### CR Campo: Transfer Type

- **instant**: El usuario eligió recibir el adelanto instantáneamente.
- **regular**: El usuario eligió no pagar inmediatamente y esperar la transferencia.

#### CR Campo: Recovery Status

- **null**: El CR nunca tuvo un incidente de pago.
- **completed**: El incidente de pago fue resuelto (el CR fue reembolsado).
- **pending**: El incidente de pago aún está abierto.
- **pending_direct_debit**: El incidente de pago sigue abierto, pero se ha lanzado un débito directo SEPA.

---

### Fees

#### Fees: Type

- **instant_payment**: Fees por adelanto instantáneo.
- **split_payment**: Fees por pago fraccionado (en caso de un incidente).
- **incident**: Fees por fallos de reembolsos.
- **postpone**: Fees por la solicitud de posponer un reembolso.

#### Fees: Status

- **confirmed**: El usuario completó una acción que creó un fee.
- **rejected**: El último intento de cobrar el fee falló.
- **cancelled**: El fee fue creado pero cancelado por algún motivo.
- **accepted**: El fee fue cobrado exitosamente.

#### Fees: Category

- **rejected_direct_debit**: Fees creados cuando el banco del usuario rechaza el primer débito directo.
- **month_delay_on_payment**: Fees creados cada mes hasta que el incidente se cierre.

#### Fees: Charge Moment

- **before**: El fee se cobra en el momento de su creación.
- **after**: El fee se cobra cuando el CR es reembolsado.

---

## Discoveries and Assumptions

- **Inicio de la BBDD de Fees**: La base de datos de fees comienza con su primer registro el 29/05/2020, siete meses después del primer registro en la tabla de CR (01/11/2019). Esto indica que los fees comenzaron a ser cobrados siete meses después de que se iniciaron las operaciones de los CR. Además, la numeración de los IDs en la tabla de fees confirma que no hay datos faltantes.




