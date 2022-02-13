FROM node

RUN apt update

#Install opencv4nodejs
# RUN apt install -y build-essential
# RUN apt install -y cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
# RUN apt install -y python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev

# ENV NODE_PATH=/usr/lib/node_modules
# RUN npm install --save opencv4nodejs

# RUN npm i -f nodemon

# ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/opencv/build/lib

WORKDIR /app
COPY . /app
RUN npm install


CMD ["npm", "start"]