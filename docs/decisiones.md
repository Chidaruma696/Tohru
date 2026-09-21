# Decisiones

Por qué Tohru es como es. Lo apunto aquí para no tener que volver a pensarlo cada vez que me pregunto "¿y esto por qué?".

## Dos esquemas, no uno (2026-09-08)

El pesable clásico (`[prefijo][PLU][peso]`) es lo que traen las básculas de fábrica y no necesita base de datos para cobrar. Pero dos paquetes iguales comparten código, así que no puedes anular uno, contar piezas ni saber cuál se vendió. El de identidad (`[prefijo][PLU][secuencia]`) resuelve eso a cambio de depender de la base.

En el negocio hacía falta rastrear cada paquete, así que identidad es el esquema principal. El pesable se queda porque hay etiquetas viejas y básculas que solo saben imprimir eso.

## Cadenas, nunca enteros

Un código `0890050490063` convertido a entero pierde el cero de delante y ya no es el mismo código. Todo trabaja sobre cadenas de dígitos. Es más incómodo pero es correcto.

## La secuencia se reserva antes de guardar

Pides el siguiente número a tu base, y guardas la fila ya con su código. Si primero guardas y luego calculas el código, hay un momento en que existe una pesada sin código que un lector no puede encontrar. Me pasó.

## Cinco dígitos de secuencia y aviso de vuelta

Cien mil códigos por prefijo. Al ritmo de una tienda chica dura más de un año, pero no es infinito, por eso `estado_secuencia` te dice cuánto queda. Cuando se acerque, se cambia de prefijo; no hay reset automático porque eso es justo lo que rompe la identidad.

## Prefijos 07 y 08

GS1 reserva 20 a 29 para uso interno, y ahí ya estaban los pesables de la báscula. 07 y 08 no chocan con nada que se venda en el negocio. Son solo el valor por defecto; la librería acepta cualquier par de dígitos.

## `decodificar` no comprueba el verificador

A propósito. Hay lectores que entregan 12 dígitos sin verificador, y rechazarlos dejaría etiquetas ilegibles. `descomponer` (identidad) sí lo exige porque ahí un dígito mal significa otro paquete. La CLI (`python -m tohru`) sí lo comprueba cuando le das 13 dígitos, porque si los tecleas a mano quieres saberlo.

## Sin dependencias

Son funciones puras sobre cadenas. Meter una librería de códigos de barras para esto era matar moscas a cañonazos, y quería poder pegarlo dentro de cualquier proyecto sin arrastrar nada.

## Lo que no me convence todavía

- `decodificar` acepta cualquier prefijo de dos dígitos que no sea de identidad, así que un EAN comercial normal sale como "pesable" con un peso absurdo. Habría que limitar a 20-29 por defecto, pero no sé si alguna báscula usa otro. Ver #2.
- Nada de esto está probado con un lector físico desde que lo saqué del sistema anterior. Ver #2.
