import aiohttp


async def get(
    url: str, headers: dict | None = None, params: dict | None = None
) -> dict:
    assert url, "URL is required"
    async with aiohttp.ClientSession() as session:
        print("================================================")
        print("GET ", url)
        print("================================================")
        async with session.get(url, headers=headers, params=params) as response:
            return await response.json()


async def post(
    url: str, headers: dict | None = None, data: dict | None = None, decode=True
) -> dict | str:
    assert url, "URL is required"
    async with aiohttp.ClientSession() as session:
        print("================================================")
        print("POST ", url)
        print("================================================")
        async with session.post(url, headers=headers, json=data) as response:
            if decode:
                return await response.json()
            return await response.text()


async def patch(
    url: str, headers: dict | None = None, data: dict | None = None, decode=True
) -> dict | str:
    assert url, "URL is required"
    async with aiohttp.ClientSession() as session:
        print("================================================")
        print("PATCH ", url)
        print("================================================")
        async with session.patch(url, headers=headers, json=data) as response:
            if decode:
                return await response.json()
            return await response.text()


async def delete(
    url: str, headers: dict | None = None, data: dict | None = None, decode=True
) -> dict | str:
    assert url, "URL is required"
    async with aiohttp.ClientSession() as session:
        print("================================================")
        print("DELETE ", url)
        print("================================================")
        async with session.delete(url, headers=headers, json=data) as response:
            if decode:
                return await response.json()
            return await response.text()