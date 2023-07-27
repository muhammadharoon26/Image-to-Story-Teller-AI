from typing import Union
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from Image2Movie import ImageToStory
import asyncio
import os
import uuid
import shutil
 
EXPORTDIR = "client"

 
app = FastAPI()

app.mount("/export", StaticFiles(directory="export"), name="export")

async def delete_folder_after_delay(folder_path: str, video_path: str, delay_seconds: int):
    await asyncio.sleep(delay_seconds)
    # Remove Folder
    shutil.rmtree(folder_path)
    # Remove Video file
    os.remove(video_path)
    print("Deleted Following Files:\n   Folder: {}\n    File: {}".format(folder_path, video_path))

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
 
 
@app.post("/upload/")
async def upload_image(request: Request, background_tasks: BackgroundTasks, image: UploadFile = File(...)):
    try:
        user_folder_name = "{}{}".format(str(uuid.uuid4()), image.filename.split(".")[-1])
        user_folder_path = EXPORTDIR + "/" + user_folder_name
        uploaded_path = user_folder_path + "/{}.{}".format(str(uuid.uuid4()), image.filename.split(".")[-1])

        if not os.path.exists(user_folder_path):
            os.makedirs(user_folder_path)
            print(f"Folder created: {user_folder_path}")
        else:
            print(f"Folder already exists: {user_folder_path}")

        # Save the uploaded image to a specific location
        with open(uploaded_path, "wb") as f:
            f.write(await image.read())
        
        agent = ImageToStory()
        export_video_path = agent.driver(uploaded_path, export_name=user_folder_name)

        # Delete the temporary file after use
        os.remove(uploaded_path)

        # Use background_tasks to run the deletion asynchronously
        background_tasks.add_task(delete_folder_after_delay, user_folder_path, export_video_path, 120)
        
        video_url = "http://" + str(request.url).split("/")[2] + "/" + export_video_path
        print("![New Video Generated]!:",video_url)

        return {
            "message": "Video Made Successfully!",
            # "video_url": "http://127.0.0.1:3000/export/{}.mp4".format(user_folder_name),
            "video_url": video_url,
            "Attention": f"Folder {user_folder_path} will be deleted after 120 seconds."
            }
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "An error occurred", "detail": str(e)})
 
@app.get("/exports/{user_id}")
def get_video(user_id: str):
    video_url = "/export/{}.mp4".format(user_id)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Video Player</title>
    </head>
    <body>
        <video width="640" height="480" controls>
            <source src="{video_url}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# def save_upload_file(upload_file: UploadFile, destination: Path) -> None:
#     try:
#         with destination.open("wb") as buffer:
#             shutil.copyfileobj(upload_file.file, buffer)
#     finally:
#         upload_file.file.close()


# def save_upload_file_tmp(upload_file: UploadFile) -> Path:
#     try:
#         suffix = Path(upload_file.filename).suffix
#         with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
#             shutil.copyfileobj(upload_file.file, tmp)
#             tmp_path = Path(tmp.name)
#     finally:
#         upload_file.file.close()
#     return tmp_path


# def handle_upload_file(upload_file: UploadFile, handler: Callable[[Path], None]) -> None:
#     tmp_path = save_upload_file_tmp(upload_file)
#     try:
#         handler(tmp_path)  # Do something with the saved temp file
#     finally:
#         tmp_path.unlink()  # Delete the temp file