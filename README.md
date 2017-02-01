1. Install Anaconda 2
$ wget https://repo.continuum.io/archive/Anaconda2-4.3.0-Linux-x86_64.sh
$ bash Anaconda2-4.3.0-Linux-x86_64.sh

2. Install sen2cor
$ wget http://step.esa.int/thirdparties/sen2cor/2.3.0/sen2cor-2.3.0.tar.gz
$ tar -xvzf sen2cor-2.3.0.tar.gz
$ cd sen2cor-2.3.0
$ python setup.py install

3. Download https://github.com/kraftek/awsdownload
$ cd ~
$ wget https://github.com/kraftek/awsdownload/releases/download/1.3-beta2/ProductDownload-1.3-beta.zip
$ unzip ProductDownload-1.3-beta.zip -d ProductDownload

4. Install ubuntu-GIS/gdal
$ sudo add-apt-repository ppa:ubuntugis/ppa && sudo apt-get update
$ sudo apt-get install gdal-bin

5. Add code below to the end of the .bashrc file
# added by Anaconda2 4.2.0 installer
export PATH="/home/ubuntu/anaconda2/bin:$PATH"

export SEN2COR_HOME=/home/ubuntu/sen2cor
export SEN2COR_BIN=/home/ubuntu/anaconda2/lib/python2.7/site-packages/sen2cor-2.3.0-py2.7.egg/sen2cor
export GDAL_DATA=/home/ubuntu/anaconda2/lib/python2.7/site-packages/sen2cor-2.3.0-py2.7.egg/sen2cor/cfg/gdal_data

# override PATH for GDAL commands
export PATH=/usr/bin:$PATH

6. Activate new PATHs
$ source ~/.bashrc

7. Install peewee and psycopg2
$ pip install peewee psycopg2
