from typing import List

from fastapi import APIRouter, Request, Body, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from bson.objectid import ObjectId

from models.student_model import StudentModel, StudentWithId, UpdateStudentModel

student_router = APIRouter()


@student_router.post(
    "/",
    response_description="Add new student",
    response_model=StudentWithId,
    status_code=201,
)
async def create_student(request: Request, student: StudentModel = Body(...)):
    student = jsonable_encoder(student)
    new_student = await request.app.mongodb["students"].insert_one(student)
    created_student: StudentWithId = await request.app.mongodb["students"].find_one(
        {"_id": new_student.inserted_id}
    )

    return created_student


@student_router.get(
    "/", response_description="List all students", response_model=List[StudentWithId]
)
async def list_students(request: Request):
    students = await request.app.mongodb["students"].find().to_list(1000)
    return students


@student_router.get(
    "/{id}", response_description="Get a single student", response_model=StudentWithId
)
async def show_student(request: Request, id: str):
    o_id = ObjectId(id)
    if (
        student := await request.app.mongodb["students"].find_one({"_id": o_id})
    ) is not None:
        return student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


@student_router.delete("/{id}", response_description="Delete a student")
async def delete_student(request: Request, id: str):
    o_id = ObjectId(id)
    delete_result = await request.app.mongodb["students"].delete_one({"_id": o_id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


@student_router.patch("/{id}", response_description="Update car")
async def update_student(
    id: str, request: Request, student: UpdateStudentModel = Body(...)
):
    o_id = ObjectId(id)
    await request.app.mongodb["students"].update_one(
        {"_id": o_id}, {"$set": student.model_dump(exclude_unset=True)}
    )

    if (
        student := await request.app.mongodb["students"].find_one({"_id": o_id})
    ) is not None:
        return StudentWithId(**student)

    raise HTTPException(status_code=404, detail=f"Student with {id} not found")
