"""Idempotent database seeding: inserts sample menu items if the menu is empty.

Run with: python -m app.seed
"""
import asyncio

from sqlalchemy import select, func

from app.database import SessionLocal
from app.llm_versions import DEFAULT_SYSTEM_PROMPT_NAME, DEFAULT_SYSTEM_PROMPT_TEMPLATE, DEFAULT_SYSTEM_PROMPT_VERSION
from app.models import MenuItem
from app.services import prompts

SAMPLE_DRINKS = [
    # --- Cafe (5) ---
    {
        "name": "Classic Espresso",
        "description": "A bold, concentrated shot of pure coffee.",
        "ingredients": ["espresso"],
        "price": 2.50,
        "category": "cafe",
    },
    {
        "name": "Caramel Latte",
        "description": "Smooth espresso with steamed milk and sweet caramel syrup.",
        "ingredients": ["espresso", "milk", "caramel syrup"],
        "price": 4.50,
        "category": "cafe",
    },
    {
        "name": "Hazelnut Cappuccino",
        "description": "Foamy cappuccino with a nutty hazelnut twist.",
        "ingredients": ["espresso", "milk", "hazelnut syrup"],
        "price": 4.75,
        "category": "cafe",
    },
    {
        "name": "Iced Americano",
        "description": "Espresso over ice with cold water — crisp and refreshing.",
        "ingredients": ["espresso", "water", "ice"],
        "price": 3.00,
        "category": "cafe",
    },
    {
        "name": "Oat Milk Mocha",
        "description": "Chocolatey mocha made dairy-free with creamy oat milk.",
        "ingredients": ["espresso", "oat milk", "cocoa", "sugar"],
        "price": 5.00,
        "category": "cafe",
    },
    # --- Tea (5) ---
    {
        "name": "Jasmine Green Tea",
        "description": "Delicate green tea scented with jasmine blossoms.",
        "ingredients": ["green tea", "jasmine"],
        "price": 3.00,
        "category": "tea",
    },
    {
        "name": "Classic Milk Tea",
        "description": "Black tea blended with milk and a touch of sugar.",
        "ingredients": ["black tea", "milk", "sugar"],
        "price": 3.75,
        "category": "tea",
    },
    {
        "name": "Iced Peach Oolong",
        "description": "Fragrant oolong tea with sweet peach, served over ice.",
        "ingredients": ["oolong tea", "peach syrup", "ice"],
        "price": 4.25,
        "category": "tea",
    },
    {
        "name": "Chamomile Honey Tea",
        "description": "Caffeine-free chamomile infusion sweetened with honey.",
        "ingredients": ["chamomile", "honey"],
        "price": 3.25,
        "category": "tea",
    },
    {
        "name": "Matcha Latte",
        "description": "Earthy ceremonial matcha whisked with steamed milk.",
        "ingredients": ["matcha", "milk", "sugar"],
        "price": 4.95,
        "category": "tea",
    },
    # --- Fruit juice (4) ---
    {
        "name": "Fresh Orange Juice",
        "description": "100% freshly squeezed oranges, nothing else.",
        "ingredients": ["orange"],
        "price": 4.00,
        "category": "fruit juice",
    },
    {
        "name": "Watermelon Cooler",
        "description": "Ice-cold blended watermelon with a hint of lime.",
        "ingredients": ["watermelon", "lime", "ice"],
        "price": 4.50,
        "category": "fruit juice",
    },
    {
        "name": "Mango Smoothie",
        "description": "Thick and creamy mango smoothie made with yogurt.",
        "ingredients": ["mango", "yogurt", "honey", "ice"],
        "price": 5.50,
        "category": "fruit juice",
    },
    {
        "name": "Berry Banana Blast",
        "description": "Mixed berries and banana blended with almond milk.",
        "ingredients": ["strawberry", "blueberry", "banana", "almond milk"],
        "price": 5.75,
        "category": "fruit juice",
    },
    {
        "name": "Green Detox Juice",
        "description": "Refreshing blend of apple, cucumber, celery and ginger.",
        "ingredients": ["apple", "cucumber", "celery", "ginger"],
        "price": 5.25,
        "category": "fruit juice",
    },
    {
        "name": "Citrus Detox Cleanse",
        "description": "Lemon, turmeric and ginger detox blend to reset your morning.",
        "ingredients": ["lemon", "turmeric", "ginger", "water"],
        "price": 5.00,
        "category": "fruit juice",
    },
    # --- Protein (3) ---
    {
        "name": "Chocolate Protein Shake",
        "description": "Rich chocolate whey protein blended with milk and banana.",
        "ingredients": ["whey protein", "milk", "banana", "cocoa"],
        "price": 6.00,
        "category": "protein",
    },
    {
        "name": "Vanilla Protein Smoothie",
        "description": "Vanilla plant-based protein with oat milk and berries.",
        "ingredients": ["pea protein", "oat milk", "strawberry", "blueberry"],
        "price": 6.25,
        "category": "protein",
    },
    {
        "name": "Peanut Butter Protein Blast",
        "description": "Peanut butter and banana protein shake for post-workout recovery.",
        "ingredients": ["whey protein", "peanut butter", "banana", "milk"],
        "price": 6.50,
        "category": "protein",
    },
]


async def seed_prompt(session) -> None:
    try:
        await prompts.get_active_prompt(session, name=DEFAULT_SYSTEM_PROMPT_NAME)
        print("Active prompt already seeded, skipping.")
    except LookupError:
        await prompts.create_version(
            session,
            name=DEFAULT_SYSTEM_PROMPT_NAME,
            template=DEFAULT_SYSTEM_PROMPT_TEMPLATE,
            version=DEFAULT_SYSTEM_PROMPT_VERSION,
            activate=True,
        )
        await session.commit()
        print("Seeded initial prompt version.")


async def seed() -> None:
    async with SessionLocal() as session:
        count = await session.scalar(select(func.count(MenuItem.id)))
        if count:
            print(f"Menu already seeded ({count} items), skipping.")
        else:
            session.add_all(MenuItem(**drink) for drink in SAMPLE_DRINKS)
            await session.commit()
            print(f"Seeded {len(SAMPLE_DRINKS)} menu items.")
        await seed_prompt(session)


if __name__ == "__main__":
    asyncio.run(seed())
