# поднять проект 
git clone https://github.com/VladislavAB/StableFinanceTest.git
cd StableFinanceTest
docker compose up --build -d

# тесты
docker compose exec app pytest