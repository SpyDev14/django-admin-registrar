# Django Admin Registrar
> Has russian-locale readme version below / Есть версия на русском языке ниже

## English
> [!warning]
> This README is a "quick draft" – I'm very busy and not yet ready for the final release of the package. I plan to provide detailed documentation for each feature. Thank you for your understanding.

This package simplifies the registration of Django models in the admin site. It registers all models of a given app (`AppConfig`), allowing you to define default admin classes (`ModelAdmin`) for models and avoid having to manually register each newly added model according to project-wide rules. For example, instead of manually registering every `SingletonModel` subclass (from `django-solo`) with `SingletonModelAdmin`, you can specify in the package settings:

```python
ADMIN_REGISTRAR = {
	'ADMINS_FOR_MODELS': {
		'solo.models.SingletonModel': 'solo.admin.SingletonModelAdmin'
	}
}
```

Now, by default, all `SingletonModel` subclasses will be registered with `SingletonModelAdmin`.

The package also offers an additional feature: "hidden models". This is a special shortcut for registering a model with `HiddenAdmin` – a custom admin class that registers the model in the admin panel but does not display it in the list, allowing all CRUD operations on the model without cluttering the main model list. This is useful when you have models like "Product Characteristic Type" and "Product Characteristic" that are only used within a product, and you want to create/edit/delete them from the product change form.

## Russian / Русский
> [!warning]
> Это readme "на скорую руку" - я очень занят и ещё не готов к окончательной публикации пакета. В планах подробная документация по каждой фиче проекта. Спасибо за понимание.

Этот пакет для удобной регистрации моделей (`Model`) в админ-панели (`admin-site`) `Django`. Он регистрирует все модели переданного приложения (`AppConfig`) позволяя определить админ-классы (`ModelAdmin`) для моделей по умолчанию и не регистрировать отдельно новую добавленную модель по установленным в проекте правилам. То есть, вместо ручной регистрации каждой модели-подтипа `SingletonModel` из `django-solo` под `SingletonModelAdmin` вы можете указать в насройках пакета следующее:
```python
ADMIN_REGISTRAR = {
	'ADMINS_FOR_MODELS': {
		'solo.models.SingletonModel': 'solo.admin.SingletonModelAdmin'
	}
}
```

И теперь по умолчанию все `SingletonModel` будут регистрироваться под `SingletonModelAdmin`.

Также у проекта есть дополнительная фича: "скрытые модели". Это специальный шорткат для регистрации модели под `HiddenAdmin` - специального админ-класса, который регистрирует модель в админ панели, но не отображает её, что позволяет производить все CRUD операции над моделью, но не засорять общий список моделей. Удобно, если у вас есть модель "Тип характеристики продукта" и "Характеристика продукта", но используются они только в продукте и создавать / изменять / удалять вы их хотите из формы изменения продукта.
