from typing import List, Optional, Any

from fastapi import APIRouter, Request, Body, status, HTTPException, Depends
from fastapi.responses import JSONResponse

from models.car_model import CarBase, CarWithId, CarUpdate
from authentication import AuthHandler

from bson.objectid import ObjectId

# instantiate the Auth Handler
auth_handler = AuthHandler()

cars_router = APIRouter()


@cars_router.get("/", response_description="List all cars")
async def list_all_cars(
    request: Request,
    min_price: int = 0,
    max_price: int = 100000,
    brand: Optional[str] = None,
    page: int = 1,
) -> List[CarWithId]:
    RESULTS_PER_PAGE = 25
    skip = (page - 1) * RESULTS_PER_PAGE

    query: Any = {"price": {"$lt": max_price, "$gt": min_price}}
    if brand:
        query["brand"] = brand

    full_query = (
        request.app.mongodb["cars"]
        .find(query)
        .sort("km", -1)
        .skip(skip)
        .limit(RESULTS_PER_PAGE)
    )

    return [CarWithId(**raw_car) async for raw_car in full_query]


# get car by ID
@cars_router.get("/{id}", response_description="Get a single car")
async def show_car(request: Request, id: str) -> CarWithId:
    o_id = ObjectId(id)
    if (car := await request.app.mongodb["cars"].find_one({"_id": o_id})) is not None:
        return CarWithId(**car)
    raise HTTPException(status_code=404, detail=f"Car with {id} not found")


# create new car
@cars_router.post("/", response_description="Add new car", status_code=201)
async def create_car(
    request: Request,
    car: CarBase = Body(...),
    userId=Depends(auth_handler.auth_wrapper),
) -> CarWithId:
    car_dump = car.model_dump()
    car_dump["owner"] = ObjectId(userId)

    new_car = await request.app.mongodb["cars"].insert_one(car_dump)
    created_car = await request.app.mongodb["cars"].find_one(
        {"_id": new_car.inserted_id}
    )

    return created_car


@cars_router.patch("/{id}", response_description="Update car")
async def update_task(id: str, request: Request, car: CarUpdate = Body(...)):
    o_id = ObjectId(id)
    await request.app.mongodb["cars"].update_one(
        {"_id": o_id}, {"$set": car.model_dump(exclude_unset=True)}
    )

    if (car := await request.app.mongodb["cars"].find_one({"_id": o_id})) is not None:
        return CarWithId(**car)

    raise HTTPException(status_code=404, detail=f"Car with {id} not found")


@cars_router.delete("/{id}", response_description="Delete car")
async def delete_task(id: str, request: Request):
    o_id = ObjectId(id)
    delete_result = await request.app.mongodb["cars"].delete_one({"_id": o_id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)

    raise HTTPException(status_code=404, detail=f"Car with {id} not found")
