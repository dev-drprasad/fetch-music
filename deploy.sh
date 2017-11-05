git pull
sudo docker build -t fetch-music .
sudo docker container stop fetch-music
sudo docker rm fetch-music
sudo docker run -d -p 5000:5000 --name fetch-music fetch-music
