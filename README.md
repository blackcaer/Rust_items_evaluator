# Rust Items Evaluator

A project for evaluating Rust items from the Steam Market and Rust gambling sites. It calculates key metrics for the provided items, such as their price and real value, and displays the results in the terminal.
This project focuses on automating Rust item analysis and includes robust error handling and asynchronous data fetching for better performance.

**This is an older project, so the code may be messy and lacks full documentation—but it was a valuable learning experience in data scraping and market analysis.**

1. **Input Handling** – Accepts user input for items, gambling site data, or inventory.  
2. **Data Fetching** – Asynchronously fetches item details from external sources (e.g., Steam Market).  
3. **Item Evaluation** – Computes item metrics based on liquidity, and prices.  
4. **Result Display** – Outputs the evaluated data to the terminal.  

## Modes:
- `EVAL_ITEMS = 1` – Evaluate specified Rust items.  
- `EVAL_RCHSHOP = 2` – Evaluate items available on Rust gambling sites.  
- `EVAL_EQ = 3` – Evaluate a provided inventory.  

## Main Files:
- **`evaluate_items.py`** – Evaluate specific Rust items from the Steam Market and display their metrics.  
- **`evaluate_rchshop.py`** – Evaluate and analyze item metrics from Rust gambling sites.  
- **`rch_evaluator.py`** – Main script combining both functionalities, supporting multiple modes and handling errors.  

## Usage:
1. Run `rch_evaluator.py`.  
2. Choose the desired evaluation mode:
    - `1` – Evaluate Rust items.  
    - `2` – Evaluate Rust gambling site items.  
    - `3` – Evaluate an inventory.  
3. Enter the required item details.  
4. View the calculated item metrics in the terminal.  

Some modes requires data to be put in another file as json. 

No support is provided since it was project for personal use only.

Some modules may, or not not be publicly present on my github such as ItemRustDatabase, ItemRustDatabaseRecord, ItemRust etc.
