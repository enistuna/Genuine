import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from src.backend.database import engine, SessionLocal, get_db
import src.backend.models as models
import src.backend.schemas as schemas
from src.backend.models import User, Account, Transaction, UserProfile, AccountType
from faker import Faker
import random
from decimal import Decimal

from src.utils.logger import setup_logger
from src.handlers.error_handler import global_exception_handler, http_exception_handler



logger = setup_logger("backend_api")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

def seed_db(db: Session):
    if db.query(User).first():
        return

    fake = Faker('tr_TR')
    logger.info("Seeding database...")
    
    users = []
    
    test_user = User(
        username="test_user",
        full_name="Test Kullanıcısı",
        password_hash="hashed_secret",
        tckn="12345678901"
    )
    db.add(test_user)
    users.append(test_user)

    for _ in range(50):        
        map_chars = {'ç':'c', 'ğ':'g', 'ı':'i', 'ö':'o', 'ş':'s', 'ü':'u', 'Ç':'c', 'Ğ':'g', 'İ':'i', 'Ö':'o', 'Ş':'s', 'Ü':'u'}
        clean_name = fake.name().lower().translate(str.maketrans(map_chars)).replace(' ', '')
        username = clean_name + str(random.randint(10, 99))
        tckn = fake.ssn()

        user = User(
            username=username,
            full_name=fake.name(),
            password_hash="hashed_secret",
            tckn=tckn
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    
    for user in users:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

        for _ in range(random.randint(1, 3)):
            acc = Account(
                user_id=user.id,
                account_type=random.choice(list(AccountType)),
                balance=Decimal(random.uniform(100, 50000)),
                iban=fake.iban()
            )
            db.add(acc)
            
    db.commit()
    logger.info(f"Database is populated with {len(users)} users.")

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    seed_db(db)
    db.close()
    logger.info("Backend API started.")

def get_user_by_tckn_helper(db: Session, tckn: str):
    return db.query(models.User).filter(models.User.tckn == tckn).first()


@app.get("/")
def read_root():
    return {"message": "Genuine Backend API (Turkish)"}

@app.get("/users/tckn/{tckn}")
def get_user_by_tckn(tckn: str, db: Session = Depends(get_db)):
    
    user = get_user_by_tckn_helper(db, tckn)
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    
    total_balance = sum(acc.balance for acc in user.accounts)
    return {
        "user_id": user.id,
        "full_name": user.full_name,
        "balance": float(total_balance),
        "accounts": [{"type": a.account_type, "balance": float(a.balance), "IBAN": a.iban} for a in user.accounts]
    }

@app.post("/transfer")
def transfer_funds(request: schemas.TransferRequest, db: Session = Depends(get_db)):
    sender = get_user_by_tckn_helper(db, request.sender_tckn)
    if not sender:
        raise HTTPException(status_code=404, detail="Gönderici bulunamadı.") 

    recipient = get_user_by_tckn_helper(db, request.recipient_tckn)
    if not recipient:
        raise HTTPException(status_code=404, detail="Alıcı bulunamadı.")

    # sender
    sender_acc = None
    for acc in sender.accounts:
        if acc.balance >= request.amount:
            sender_acc = acc
            break
    
    if not sender_acc:
        raise HTTPException(status_code=400, detail="Yetersiz bakiye.")
        
    # recipient
    recipient_acc = recipient.accounts[0] if recipient.accounts else None
    if not recipient_acc:
         raise HTTPException(status_code=400, detail="Alıcı hesap bulunamadı.")

    sender_acc.balance -= request.amount
    recipient_acc.balance += request.amount
    
    tx_sender = models.Transaction(
        amount=-request.amount,
        description=f"Transfer: {recipient.full_name} kişisine",
        from_account_id=sender_acc.id,
        to_account_id=recipient_acc.id
    )
    tx_recipient = models.Transaction(
        amount=request.amount,
        description=f"Transfer: {sender.full_name} kişisinden",
        from_account_id=sender_acc.id,
        to_account_id=recipient_acc.id
    )
    
    db.add(tx_sender)
    db.add(tx_recipient)
    db.commit()
    
    logger.info(f"Transfer successful: {sender.tckn} -> {recipient.tckn} Amount: {request.amount}")

    return {
        "mesaj": "Transfer işlemi başarıyla gerçekleşti", 
        "yeni_bakiye": float(sender_acc.balance)
    }

@app.get("/users/{user_id}/transactions")
def list_transactions(user_id: int, db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
        
    account_ids = [acc.id for acc in user.accounts]
    
    transactions = db.query(Transaction).filter(
        (Transaction.from_account_id.in_(account_ids)) | 
        (Transaction.to_account_id.in_(account_ids))
    ).order_by(Transaction.timestamp.desc()).limit(10).all()
    
    result = []
    for t in transactions:
        show_tx = False
        display_amount = float(t.amount)
        
        if t.from_account_id in account_ids and t.amount < 0:
            show_tx = True
        elif t.to_account_id in account_ids and t.amount > 0:
            show_tx = True
            
        if show_tx:
            result.append({
                "date": t.timestamp.strftime("%Y-%m-%d"),
                "description": t.description,
                "amount": display_amount
            })
        
    return {"transactions": result}

@app.get("/users/{user_id}/profile")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profil bulunamadı.")
    return {
        "interaction_count": profile.interaction_count,
        "financial_literacy_score": profile.financial_literacy_score,
        "preferred_tone": profile.preferred_tone
    }


@app.post("/users/{user_id}/log_interaction")
def log_interaction(user_id: int, body: dict, db: Session = Depends(get_db)):

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        return {"status": "error", "detail": "Profil bulunamadı"}
        
    profile.interaction_count += 1
    
    topic = body.get("topic")
    if topic in ["stocks", "interest_rates", "investment"]:
        profile.financial_literacy_score = min(100, profile.financial_literacy_score + 1)
        
    if body.get("used_slang"):
        profile.preferred_tone = "friendly"
        
    db.commit()
    return {"status": "updated", "profile": get_user_profile(user_id, db)}