# Multi-Currency Interest Rate Calibration and Stress Testing Framework
## Overview
A python-based framework for generating synthetic interest rate market data, calibrating short-rate models, performing stress testing and visualizing results across multiple currencies.
The project demonstrates quantitative model development, data engineering practices, configuration-driven design and containerized deployment using Docker.
## Key Features
-  Multi-currency yield curve generation
-  Historical risk-free rate simulation
-  ATM European Swaption Volatility Surface generation
-  Scenario-based Stress Testing
-  Vasicek model calibration
-  Hull-White model calibration
-  Streamlit dashboard visualization
-  Dockerized deployment
## Project Structure
```Mermaid
flowchart TD
A[Currency Configuration]
B[Curve Generation]
C[Volatility Surface]
D[Historical RFR Generation]
E[Vasicek Calibration]
F[Hull White Calibration]
G[visualization Dashboard]
A -->B
A -->C
A-->D
D-->E
B-->E
B-->F
C-->F
F-->G
E-->G
```
## Technologies
### Quantitative Models
- Vasicek Model
- Hull-White One-Factor Model
- Nelder-Mead Optimization
### Python libraries
- Numpy
- Pandas
- Scipy
- Statsmodels
- Streamlit
- PyYAML
### Engineering
- Object-Oriented Design
- Configuration-Driven Framework
- Docker
- Git
## Running the Dashboard
### Local Environment
```bash
pip install -r requirement.txt
python -m main.py
streamlit run src/visualization/visualize.py
```
### Docker
#### Build image:
```bash
docker build -t ir-dashboard:1.0 .

```
#### Run container:
```bash
docker run -p 8501:8501 ir-dashboard:1.0
```
#### Open:
```Plain text
http://localhost:8501
```
## Future Enhancement
- Trinomial Tree Interest Rate Engine
- Monte Carlo Interest Rate Engine
- Bermudan Swaption Pricing
- American Bond Option Pricing
- Cap/Floor Valuation
- PostgreSQL Data Storage
- Spark-based Distributed Processing
- CI/CD Deployment

