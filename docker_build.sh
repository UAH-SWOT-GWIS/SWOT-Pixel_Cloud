docker build -t swot .
docker stop swot
docker rm swot
docker run -d --name swot-container -p 8000:8000 swot
