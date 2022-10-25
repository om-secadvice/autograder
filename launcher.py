
import argparse
from os import remove, path
import tarfile
from io import BufferedRWPair, BufferedReader, DEFAULT_BUFFER_SIZE,RawIOBase
from tempfile import NamedTemporaryFile
from re import compile
from os import getpid,getppid
import random
import docker,os
from time import sleep
client=docker.from_env()

VOLUME_NAME=os.environ['DOCKER_VOLUME_BASE_NAME']#grader_volume
CONTAINER_NAME=['DOCKER_CONTAINER_BASE_NAME']#grader_container
IMAGE_NAME=os.environ['DOCKER_IMAGE_NAME'] #grader_python
WORKDIR=os.environ['CONTAINER_WORKDIR'] #/home/appuser/script/
OUTPUT_DIR=os.environ['REPORT_OUTPUT_DIR'] #'/'
MAX_CONTAINERS=5
def get_or_create_volume():
    try:
        volume=client.volumes.get(VOLUME_NAME)
    except docker.errors.NotFound:
        volume=client.volumes.create(name=VOLUME_NAME)
    return volume

def get_or_run_container(volume):
    global CONTAINER_NAME,MAX_CONTAINERS
    try_again=True
    container_number=str(random.randint(1,5)) 
    while(try_again):
        try:
            container=client.containers.run(IMAGE_NAME,volumes={volume.name:{'bind':WORKDIR,'mode':'rw'}},name=CONTAINER_NAME+container_number,tty=True,command='/bin/sh',detach=True)
            try_again=False
        except:
            try:
                container=client.containers.get(CONTAINER_NAME+container_number)
                try_again=False
            except:
                try_again=True
    
    container.reload()
    if container.status=="exited":
        container.start()
    while(container.status!="running"):
        container.reload()
    return container

"""Logic to transfer files
between Host and container"""
def generator_to_stream(generator, buffer_size=DEFAULT_BUFFER_SIZE):
    class GeneratorStream(RawIOBase):
        def __init__(self):
            self.leftover = None

        def readable(self):
            return True

        def readinto(self, b):
            try:
                l = len(b)  # : We're supposed to return at most this much
                chunk = self.leftover or next(generator)
                output, self.leftover = chunk[:l], chunk[l:]
                b[:len(output)] = output
                return len(output)
            except StopIteration:
                return 0  # : Indicate EOF
    return BufferedReader(GeneratorStream())

def copy_from_container(container, src, dest, bufsize):
    """Method to copy file from container to local filesystem"""
    tar_name = None
    with NamedTemporaryFile(buffering=bufsize, prefix="dockercp", delete=False) as f:
        tar_name = f.name
        archive = container.get_archive(src)
        
        buff = BufferedRWPair(generator_to_stream(archive[0]), f, bufsize)
        # read the data (an archive) sent by docker daemon into a temporary file locally
        while True:
            if buff.write(buff.read(bufsize)) < bufsize:
                break
        buff.flush()
    # let's extract the archive into the destination
    with tarfile.open(tar_name,mode="r|", bufsize=bufsize) as tar:
        
        import os
        
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, path=dest)
        remove(tar_name)

def copy_to_container(container, src, dest, bufsize):
    """Method to copy file from local file system into container"""
    # it's necessary create a tar file with src file/directory
    archive = None
    with NamedTemporaryFile(buffering=bufsize, prefix="dockercp", delete=False) as fp:
        with tarfile.open(mode="w|",fileobj=fp, bufsize=bufsize) as tar:
            tar.add(src, arcname=path.basename(src))
        archive = fp.name
    # send the tar to the container
    if archive is not None:
        result = False
        with open(archive, "rb", buffering=bufsize) as fp:
            result = container.put_archive(dest, fp)
        remove(archive)
        return result
    return False

def filename(name,extension):
    return name+"."+extension
def grade_file(file):
    volume=get_or_create_volume()
    container=get_or_run_container(volume)



    name=file["full_name"].split('.')[0]
    extension=file["full_name"].split('.')[-1]
    print(name,extension,sep='.')
    copy_to_container(container,
                    file["path"]+'/'+filename(name,extension),
                    WORKDIR,
                    DEFAULT_BUFFER_SIZE)
    
    container.exec_run('./autograder.sh {} {}'.format(name,container.id))
    flag=True
    i=0
    while(flag and i<5):
        try:
            # sleep(2)
            copy_from_container(container,
                                WORKDIR+filename(name,'output'),
                                file["path"]+OUTPUT_DIR,
                                DEFAULT_BUFFER_SIZE)
            flag=False
        except:
            flag=True
            i+=1




