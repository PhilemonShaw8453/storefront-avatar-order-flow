import uvicorn


if __name__ == "__main__":
    uvicorn.run("storefront_avatar.avatar_service:app", host="127.0.0.1", port=8000)

