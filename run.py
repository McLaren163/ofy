import sys
from app import app


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'init_db':
        from app.utils import db_init
        db_init()
        exit()
    app.run(debug=True)
