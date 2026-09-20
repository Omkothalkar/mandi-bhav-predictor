class DecisionEngine:
    @staticmethod
    def calculate_transport_cost(distance_km: float, transport_rate: float, quantity: float, quantity_unit: str) -> float:
        """
        Calculates transport cost.
        quantity_unit must be 'quintals' or 'tonnes'.
        Dataset price is Rs/Quintal. So transport rate should be Rs/km/Quintal.
        """
        # Convert tonnes to quintals
        quantity_quintals = quantity
        if quantity_unit == 'tonnes':
            quantity_quintals = quantity * 10
            
        cost = distance_km * transport_rate * quantity_quintals
        return round(cost, 2)
        
    @staticmethod
    def calculate_net_return(expected_price_per_quintal: float, quantity: float, quantity_unit: str, transport_cost: float) -> tuple:
        """
        Calculates gross revenue and net return.
        """
        quantity_quintals = quantity
        if quantity_unit == 'tonnes':
            quantity_quintals = quantity * 10
            
        gross_revenue = expected_price_per_quintal * quantity_quintals
        net_return = gross_revenue - transport_cost
        return round(gross_revenue, 2), round(net_return, 2)

    @staticmethod
    def generate_decision(current_net_return: float, forecast_net_return: float, threshold_percent: float = 2.0) -> tuple:
        """
        SELL / WAIT decision engine.
        Rule: 
        Wait if forecast_net_return is significantly better than current_net_return.
        Otherwise SELL.
        """
        if current_net_return <= 0:
            return "WAIT", "Current net return is zero or negative."
            
        pct_improvement = ((forecast_net_return - current_net_return) / current_net_return) * 100
        
        if pct_improvement > threshold_percent:
            return "WAIT", f"Forecast net return improves by {pct_improvement:.2f}%, which is above the {threshold_percent}% threshold."
        else:
            return "SELL", f"Forecast net return improvement ({pct_improvement:.2f}%) is below the {threshold_percent}% threshold."

decision_engine = DecisionEngine()
