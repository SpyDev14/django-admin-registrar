# Django Admin Registrar
1. О пакете
2. Последние изменения
3. Дорожная карта к v1.0

## О пакете
Пакет предназначен для упрощения регистрации моделей в админ-панели Django, а именно для:
1. Минимизации boiler-plate кода (никаких 10 повторяющихся для каждой модели `@register` + `class MyOrderedModelAdmin(OrderedModelAdmin)`)
2. (более глобальная задача) фиксации правил применяемых админ-классов для моделей. То есть вместо того, чтобы помнить каждый раз про использование `OrderedModelAdmin` для всех наследников `OrderedModel` один в раз в проекте указать "использовать `OrderedModelAdmin` для всех наследников `OrderedModel`.

### До
```python
@register
```

### После
```python

```

С первой задачей проект справляется отлично (не нужно регистрировать каждую модель отдельно, можно просто указать класс по умолчанию, что особенно удобно при разработке), со второй пока частично (пока либо неявная регистрация модели админ-классом по умолчанию, либо явно указанный админ-класс). Для второго в будущем планируется реализовать функционал по типу "получить админ-класс по умолчанию для модели" и использовать его при наследовании кастомного админ-класса.

This package simplifies the registration of Django models in the admin site. It registers all models of a given app (`AppConfig`), allowing you to define default admin classes (`ModelAdmin`) for models and avoid having to manually register each newly added model according to project-wide rules. For example, instead of manually registering every `SingletonModel` subclass (from `django-solo`) with `SingletonModelAdmin`, you can specify in the package settings:

```python
# settings.py
ADMIN_REGISTRAR = {
    'ADMINS_FOR_MODELS': {
        'solo.models.SingletonModel': 'solo.admin.SingletonModelAdmin'
    }
}
```
```python
# admin.py
from admin_registrar import AdminRegistrar
from src.apps.products.apps import ProductsConfig

registrar = AdminRegistrar(ProductsConfig)
registrar.register()
```

Now, by default, all `SingletonModel` subclasses will be registered with `SingletonModelAdmin`.

The package also offers an additional feature: "hidden models". This is a special shortcut for registering a model with `HiddenAdmin` – a custom admin class that registers the model in the admin panel but does not display it in the list, allowing all CRUD operations on the model without cluttering the main model list. This is useful when you have models like "Product Characteristic Type" and "Product Characteristic" that are only used within a product, and you want to create/edit/delete them from the product change form.

For configuring autoregister `AdminRegistrar` has too many methods (and decorators). Enjoy!

## Крупный релиз v0.3!
### ✨ Добавлено
- `AdminRegistrar` регистрация теперь выводит предупреждение при попытке регистрации **уже** зарегистрированной модели.
- Добавлен протокол `AdminRegistry`: теперь регистрация и проверка статуса регистрации осуществляется не через прямой доступ к `site` из `django.contrib.admin`, а через абстрактный "админ реестр". Вы можете подменить обращение к `site` (соответствует протоколу, используется напряму) на свою реализацию, соответствующую `AdminRegistry`.
- Добавлен метод `AdminRegistry.defer_registration()`: теперь вы можете запланировать регистрацию на момент вызова вашего `MyAppConfig.ready()` (атрибут `MyAppConfig.ready` будет заменён на спец-прослойку с вызовом `AdminRegistrar.register()`). Ранее вам приходилось добавлять импорт и вызов `register()` в `MyAppConfig.ready()` вручную.
- Добавлена поддержка локальных переопределений для `Config`: теперь вы можете переопределить значение конфига и передать его явно в конструктор `AdminRegistrar` через kwarg-only параметр `config`. Ранее каждый используемый `CVar` дублировался как kwarg-only параметр конструктора `AdminRegistrar`.
- Добавлены system-checks: теперь проверяется, что все ключи в `settings.ADMIN_REGISTRAR` известны, а также что все указанные параметры валидны.

### 🔁 Изменено
- Параметр `COLORED_LOGS` переименован в `ENABLE_COLORED_LOGS` и новым знчением по умолчанию теперь является `True` (было `False`). Это не ломающее изменение (так как изменилось значение по умолчанию), но теперь вы будете видеть предупреждение о неизвестном ключе в конфиге. Также, если вам не нужны цветные логи, вам нужно будет явно установить `False`.
- Попытка провести регистрацию после того, как она уже была проведена, теперь вызывает исключение `RuntimeError`, а не выводит предупреждение.

## Дорожная карта к v1.0
- Добавить подробную документацию (расширить docstrings, добавить re-docs / аналоге)
- Добавить автотесты
- Добавить поддержку регистрации сразу нескольких приложений (например `admin.py` в папке проекта, а не для конкретного приложения), для удобной работы с проектами с маленькими приложениями, чтобы не добавлять явный `admin.py` с созданием там `AdminRegistrar`
- Добавить резолвер классов по умолчанию с поддержкой спецификаторов вида "`Модель1 + Модель2`" (применить к моделям, наследующимся от Модель1 И от Модель2) вместо примитивного первого метча по MRO. Сейчас невозможно определить админ-класс по умолчанию для моделей со множественным наследованием (от базовых моделей или миксинов).
- Добавить "патч" админ-классы, или просто метод `AdminRegistrar.get_default_admin(type[Model]) -> type[ModelAdmin]` (в сочетании с `AdminRegistrar.set_for_model`), чтобы объединять админ-класс по умолчанию с админ-классом с определниями для конкретной модели. Сейчас нужно определять админ-класс явно и устанавливать его для конкретной модели.
- Возможно, добавить генерацию админ-классов: условный спецификатор `Model1Admin + Model2Admin` вместо ручного создания `Model12Admin`. Например, `SingletonAdmin + PagedModelAdmin` автоматически создаст админ-класс наследующийся от `SingletonAdmin` и `PagedModelAdmin` (`admin_class = type(..., (SingletonAdmin, PagedModelAdmin), ...)`) вместо явно созданного в проекте `class SingletonPagedAdmin(SingletonAdmin, PagedModelAdmin)`.
