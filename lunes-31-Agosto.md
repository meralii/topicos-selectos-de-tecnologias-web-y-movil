Java
Paradigma: Orientado a objetos basado en clases (imperativo, concurrente).

Patrones frecuentes: Factory, Singleton, Strategy, Observer, Builder, Decorator.

Relevancia: Crítica. La arquitectura empresarial tradicional y las APIs del ecosistema Java dependen de interfaces abstractas y desacoplamiento estricto.


C++
Paradigma: Multiparadigma (OOP, procedimental, genérico/metaprogramación).

Patrones frecuentes: RAII (Resource Acquisition Is Initialization), Factory, Adapter, CRTP (Curiously Recurring Template Pattern), Observer.

Relevancia: Crítica. Patrones como RAII son esenciales para el manejo determinista de memoria y recursos del sistema sin recolector de basura.


C#
Paradigma: Multiparadigma (OOP fuertemente tipado, funcional, imperativo).

Patrones frecuentes: Dependency Injection, Repository, Observer (eventos y delegados), Factory, Async/Await.

Relevancia: Crítica. El marco .NET y Clean Architecture se estructuran sobre inyección de dependencias y patrones GoF clásicos.


TypeScript
Paradigma: Multiparadigma (OOP estructurado, funcional).

Patrones frecuentes: Adapter, Decorator, Builder, Strategy, Dependency Injection.

Relevancia: Alta. Facilita estructurar código a gran escala aplicando patrones formales de OOP sobre la base de JavaScript.


Kotlin
Paradigma: Multiparadigma (OOP, funcional).

Patrones frecuentes: Singleton (nativo con object), Delegation (nativo con by), Builder (mediante DSLs de lambdas), Strategy.

Relevancia: Alta. Varios patrones de diseño de GoF están integrados directamente en la sintaxis del lenguaje.


PHP
Paradigma: Multiparadigma (OOP, imperativo).

Patrones frecuentes: MVC, Active Record, Data Mapper, Repository, Factory, Singleton.

Relevancia: Alta. Los frameworks web dominantes (como Laravel o Symfony) estructuran todo el ciclo de petición-respuesta con patrones.


Swift
Paradigma: Multiparadigma (orientado a protocolos, OOP, funcional).

Patrones frecuentes: Delegation, Protocol-Oriented, Singleton, MVC / MVVM, Target-Action.

Relevancia: Alta. Las interfaces y arquitecturas de Apple dependen operativamente del patrón delegado y la composición de protocolos.


Ruby
Paradigma: Multiparadigma (OOP puro, funcional).

Patrones frecuentes: Active Record, Metaprogramming/DSL, Monkey Patching, Decorator, Strategy.

Relevancia: Alta. Al ser todo un objeto y permitir modificar clases en tiempo de ejecución, redefine los patrones de diseño orientados a fluidez sintáctica.


Rust
Paradigma: Multiparadigma (sistemas, funcional, imperativo).

Patrones frecuentes: RAII, Builder, Newtype, Type-State pattern, Iterator, Visitor.

Relevancia: Alta (patrones específicos). Adapta las soluciones arquitectónicas a su modelo de ownership y borrowing, evitando punteros compartidos mutables.


JavaScript
Paradigma: Multiparadigma (basado en prototipos, funcional, imperativo).

Patrones frecuentes: Module Pattern, Pub/Sub, Observer, Middleware, Factory.

Relevancia: Alta. Son el núcleo para resolver asincronía, manejo de eventos en el DOM y gestión de estado reactivo.


Scala
Paradigma: Híbrido (OOP + Funcional puro).

Patrones frecuentes: Cake Pattern (inyección de dependencias), Companion Object, Monad, Factory, Visitor.

Relevancia: Alta. Une abstracciones algebraicas del paradigma funcional con patrones estructurales de orientación a objetos.





C
Paradigma: Imperativo / Procedimental.

Patrones frecuentes: Puntero opaco (encapsulamiento), Punteros a funciones (simula callbacks/Strategy), Máquinas de estado.

Relevancia: Baja. No le interesan los patrones orientados a objetos; prioriza el control directo de hardware, memoria plana y funciones simples.



Haskell
Paradigma: Funcional puro.

Patrones frecuentes: Monad, Functor, Applicative, Lens, Monoid.

Relevancia: No le importan los GoF clásicos. No tiene estado mutable ni clases de objetos; sus patrones derivan de la teoría de categorías matemáticas.


Elixir
Paradigma: Funcional, concurrente.

Patrones frecuentes: Actor Model, GenServer/Supervisor (árboles de supervisión), Pipeline (|>).

Relevancia: No le importan los GoF. Opera sobre la máquina virtual BEAM; su arquitectura gira exclusivamente en torno a procesos aislados y tolerancia a fallos.


Erlang
Paradigma: Funcional, concurrente.

Patrones frecuentes: Actor Model, Supervisor, Finite State Machine (gen_statem).

Relevancia: No le importan los GoF. Creado para telecomunicaciones y sistemas distribuidos masivos donde el concepto de objeto no aplica.


Clojure
Paradigma: Funcional (dialecto Lisp).

Patrones frecuentes: State patterns (Atoms, Refs, Agents), Reducers, Middleware.

Relevancia: No le importan los GoF. Prioriza la inmutabilidad de datos y la homoiconicidad (código es datos); las funciones puras resuelven lo que en OOP requeriría clases intermedias.


Prolog
Paradigma: Lógico / Declarativo.

Patrones frecuentes: Generate and Test, Accumulator Pattern, Difference Lists, Cut-and-Fail.

Relevancia: Totalmente ajeno. Se fundamenta en hechos, reglas, unificación y retrobúsqueda (backtracking); no existe el concepto de entidad u objeto.


Bash / Shell
Paradigma: Scripting imperativo / Procedimental.

Patrones frecuentes: Pipeline (filosofía Unix), Wrapper, Dispatcher, Filter.

Relevancia: No le importan. Diseñado para la orquestación del sistema operativo y redirección de flujos estándar de texto (stdin, stdout).




Python
Paradigma: Multiparadigma (orientado a objetos, imperativo, funcional, reflexivo).

Patrones frecuentes: Decorator (nativo con @), Iterator/Generator (yield), Singleton (mediante módulos), Strategy.

Relevancia: Moderada. Adopta patrones idiomáticos; las funciones de primera clase y el tipado dinámico vuelven obsoletos muchos patrones formales de clases.


Go (Golang)
Paradigma: Concurrente, imperativo (composición sobre herencia).

Patrones frecuentes: Options Pattern, Reader/Writer wrapper (Decorator), Worker Pool, Factory.

Relevancia: Moderada. Rechaza la herencia tradicional; prefiere interfaces implícitas, composición y canales concurrentes (goroutines).