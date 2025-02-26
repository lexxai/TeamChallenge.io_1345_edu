# Languages

Вебсайт має основну мову за змовчуванням, інші мови додаються через панель адміністратора.
А у продуктах можна вказати безпосередньо додаткові переклади текстів на інші мови.
Якщо не має перекладу буде застосована мова за змовчуванням.

![admin-languages.png](img/admin-languages.png)

## ProductTranslation 
### Translated fields:
- `name` - назва продукту
- `description` - опис продукту
- `translation` - переклад тексту на іншу мову, як посилання на `ProductTranslation`

### Admin Product Translation:
![admin_product_translation_01.png](img/admin_product_translation_01.png)

## DB Diagram Translations

![db-model-product.png](img/db-model-product.png)
![db-model-product-translation.png](img/db-model-product-translation.png)
![db_table_producttranslation.png](img/db_table_producttranslation.png)

### CategoryTranslation
![admin-category-translation-01.png](img/admin-category-translation-01.png)
![admin-category-translation-02.png](img/admin-category-translation-02.png)

### CategorySchemaTranslation
![admin-categoryshema-translation-01.png.png](img/admin-categoryshema-translation-01.png.png)

### App language
- models: 
  - `Language`
  - `ProductTranslation`
  - `CategoryTranslation`
  - `CategorySchemaTranslation`
- serializers: `ProductTranslationSerializer`
- admin: `LanguageAdmin`