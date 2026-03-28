# Users

Access users through `notion.users`.

```python
async with Notionary() as notion:
    people = await notion.users.list_users()
    bots = await notion.users.list_bots()
    me = await notion.users.me()
```

::: notionary.user.namespace.UsersNamespace

---

## Person

::: notionary.user.models.Person

---

## Bot

::: notionary.user.models.Bot

!!! info "Notion API Reference"
[Users](https://developers.notion.com/reference/get-users)
