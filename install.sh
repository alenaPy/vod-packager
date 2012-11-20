#!/bin/bash
rm packager.db
python manage.py syncdb
python create_test.py
python create_item.py
python create_path.py
