from notionary.http.client import HttpClient
from notionary.page.comments.service import PageComments
from notionary.page.content import PageContent
from notionary.page.properties import PagePropertyHandler
from notionary.page.properties.schemas import AnyPageProperty
from notionary.page.schemas import PageUpdateRequest, _DefaultTemplate, _TemplateById
from notionary.shared.entity import EntityCover, EntityIcon, EntityTrash
from notionary.shared.models.file import File
from notionary.shared.models.icon import Icon


class Page:
    def __init__(
        self,
        id: str,
        url: str,
        title: str,
        icon: Icon | None,
        cover: File | None,
        in_trash: bool,
        properties: dict[str, AnyPageProperty],
        http: HttpClient,
    ) -> None:
        self.id = id
        self.url = url
        self.title = title

        path = f"pages/{id}"
        self._http = http
        self._path = path
        self._icon = EntityIcon(icon=icon, http_client=http, path=path)
        self._cover = EntityCover(cover=cover, http_client=http, path=path)
        self._trash = EntityTrash(in_trash=in_trash, http_client=http, path=path)

        self.properties = PagePropertyHandler(properties=properties, id=id, http=http)

        self._content = PageContent(page_id=id, http=http)
        self._comments = PageComments(page_id=id, http=http)

    @property
    def in_trash(self) -> bool:
        return self._trash.in_trash

    async def trash(self) -> None:
        await self._trash.trash()

    async def restore(self) -> None:
        await self._trash.restore()

    async def set_icon_emoji(self, emoji: str) -> None:
        if self._icon:
            await self._icon.set_emoji(emoji)

    async def set_icon_url(self, url: str) -> None:
        if self._icon:
            await self._icon.set_from_url(url)

    async def remove_icon(self) -> None:
        if self._icon:
            await self._icon.remove()

    async def set_cover(self, url: str) -> None:
        if self._cover:
            await self._cover.set_from_url(url)

    async def random_cover(self) -> None:
        if self._cover:
            await self._cover.set_random_gradient()

    async def remove_cover(self) -> None:
        if self._cover:
            await self._cover.remove()

    async def append(self, content: str) -> None:
        await self._content.append(content=content)

    async def replace(self, content: str) -> None:
        await self._content.replace(content=content)

    async def clear(self) -> None:
        await self._content.clear()

    async def get_markdown(self) -> str:
        return await self._content.get_markdown()

    async def comment(self, text: str) -> None:
        await self._comments.create(text)

    async def reply_to(self, discussion_id: str, text: str) -> None:
        await self._comments.reply_to(discussion_id, text)

    async def rename(self, title: str) -> None:
        await self.properties.set_title(title)
        self.title = title

    async def lock(self) -> None:
        await self._patch(PageUpdateRequest(is_locked=True))

    async def unlock(self) -> None:
        await self._patch(PageUpdateRequest(is_locked=False))

    async def erase_content(self) -> None:
        await self._patch(PageUpdateRequest(erase_content=True))

    async def apply_default_template(
        self,
        timezone: str | None = None,
        erase_content: bool = False,
    ) -> None:
        template = _DefaultTemplate(timezone=timezone)
        await self._patch(
            PageUpdateRequest(
                template=template,
                erase_content=erase_content or None,
            )
        )

    async def apply_template(
        self,
        template_id: str,
        timezone: str | None = None,
        erase_content: bool = False,
    ) -> None:
        template = _TemplateById(template_id=template_id, timezone=timezone)
        await self._patch(
            PageUpdateRequest(
                template=template,
                erase_content=erase_content or None,
            )
        )

    async def _patch(self, request: PageUpdateRequest) -> None:
        data = request.model_dump(exclude_none=True)
        await self._http.patch(self._path, data=data)
