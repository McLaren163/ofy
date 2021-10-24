import sys
from app import app


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'init':
            from app.utils import db_init
            db_init()
        if sys.argv[1] == 'run':
            app.run(debug=True)
