import os
os.environ["AIPROXY_TOKEN"]="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDE4MTNAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.KfUvvRzTTwUNllQPs5gT6klsiXlaWdyTWcJ41avXkRM"
import sys
import pandas as pd
import matplotlib.pyplot as plt
import warnings
import openai

warnings.filterwarnings("ignore")


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run autolysis.py <dataset.csv>")
        sys.exit(1)

    csv_file = sys.argv[1]

    if not os.path.exists(csv_file):
        print(f"File not found: {csv_file}")
        sys.exit(1)

    # Load dataset
    try:
        data = pd.read_csv(csv_file,engine ='python',encoding='unicode_escape')
    except Exception as e:
        print(f"Error loading CSV: {e}")
        sys.exit(1)

    # Summary of dataset
    summary = summarize_data(data)
    print("Data summary completed.")

    # Correlation matrix and visualization
    corr_chart = "correlation_matrix.png"
    create_correlation_heatmap(data, corr_chart)
    print("Correlation heatmap created.")

    # Handle LLM
    openai.api_base = "https://aiproxy.sanand.workers.dev/openai/v1"
    openai.api_key = os.environ.get("AIPROXY_TOKEN")
    if not openai.api_key:
        print("AIPROXY_TOKEN environment variable not set.")
        sys.exit(1)

    narrative = generate_llm_analysis(data, summary)
    print("LLM analysis completed.")

    # Generate README.md
    generate_readme(narrative, [corr_chart])
    print("README.md file created.")


def summarize_data(data):
    """Generate a summary of the dataset."""
    summary = {
        "columns": data.columns.tolist(),
        "dtypes": data.dtypes.astype(str).to_dict(),
        "missing_values": data.isnull().sum().to_dict(),
        "basic_stats": data.describe(include="all").to_dict()
    }
    return summary


def create_correlation_heatmap(data, output_file):
    """Create and save a correlation heatmap."""
    numeric_data = data.select_dtypes(include="number")
    if numeric_data.empty:
        print("No numeric data for correlation heatmap.")
        return

    corr = numeric_data.corr()

    # Plotting the heatmap using matplotlib
    fig, ax = plt.subplots(figsize=(10, 8))
    cax = ax.matshow(corr, cmap="coolwarm")
    fig.colorbar(cax)

    # Setting axis labels
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="left", fontsize=8)
    ax.set_yticklabels(corr.columns, fontsize=8)

    plt.title("Correlation Heatmap", pad=20)
    plt.savefig(output_file)
    plt.close()


def generate_llm_analysis(data, summary):
    """Use OpenAI GPT-4o-Mini to generate an analysis narrative."""
    prompt = f"""
    You are a data scientist. Analyze the following dataset information and suggest key insights:
    - Column names: {summary['columns']}
    - Data types: {summary['dtypes']}
    - Missing values: {summary['missing_values']}
    - Summary statistics: {summary['basic_stats']}

    Provide a narrative for the README.md that:
    - Describes the dataset
    - Summarizes key insights
    - Recommends actionable steps based on the data.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        print(f"Error during LLM analysis: {e}")
        sys.exit(1)


def generate_readme(narrative, charts):
    """Create a README.md with the analysis narrative and charts."""
    with open("README.md", "w") as f:
        f.write("# Automated Data Analysis Report\n\n")
        f.write(narrative)
        f.write("\n\n## Visualizations\n\n")
        for chart in charts:
            f.write(f"![Visualization]({chart})\n")


if __name__ == "__main__":
    main()
