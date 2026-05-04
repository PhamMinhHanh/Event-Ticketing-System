from app import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        # --- CHÈN 3 DÒNG NÀY VÀO ĐỂ FIX LỖI DRAFT ---
        from sqlalchemy import text
        db.session.execute(text("UPDATE events SET status = 'PUBLISHED' WHERE status = 'DRAFT'"))
        db.session.commit()

        pass

    app.run(debug=True)