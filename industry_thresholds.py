industry_thresholds = {
    'Technology': {
        'pe_threshold': 30,
        'pb_threshold': 5,
        'de_threshold': 0.5,
        'current_ratio_threshold': 2.0,
        'peg_threshold': 1.0,
        'profit_margin_threshold': 15,
        'revenue_growth_threshold': 0.15
    },
    'Gold': {
        'pe_threshold': 20,
        'pb_threshold': 2,
        'de_threshold': 0.1,
        'current_ratio_threshold': 2.5,
        'peg_threshold': 1.0,
        'profit_margin_threshold': 10,
        'revenue_growth_threshold': 0.05
    },
    'Healthcare': {
        'pe_threshold': 25,
        'pb_threshold': 3,
        'de_threshold': 1.0,
        'current_ratio_threshold': 1.5,
        'peg_threshold': 1.5,
        'profit_margin_threshold': 12,
        'revenue_growth_threshold': 0.10
    },
    'Consumer Goods': {
        'pe_threshold': 20,
        'pb_threshold': 3,
        'de_threshold': 1.5,
        'current_ratio_threshold': 1.5,
        'peg_threshold': 1.0,
        'profit_margin_threshold': 10,
        'revenue_growth_threshold': 0.10
    }
}

def get_thresholds(industry):
    return industry_thresholds.get(industry, {})