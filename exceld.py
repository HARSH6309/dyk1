from flask import Flask, jsonify, request
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/dyk-entries', methods=['GET'])
def get_dyk_entries():
    try:
        # Get the date parameter from the URL (format: DD-MM)
        date_param = request.args.get('date')
        
        # Path to the Excel file
        file_path = os.path.join(os.path.dirname(__file__), 'New-API.xlsx')

        
        if not os.path.exists(file_path):
            return jsonify({'message': 'Excel file not found'}), 404
            
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Filter the data if date parameter is provided
        if date_param and len(date_param) == 5 and date_param[2] == '-':
            try:
                day, month = map(int, date_param.split('-'))
                
                # Define a function to match day and month
                def match_date(date_val):
                    try:
                        if pd.isna(date_val):
                            return False
                        
                        if isinstance(date_val, str):
                            # Try to parse as string (YYYY-MM-DD)
                            date_obj = datetime.strptime(date_val, '%Y-%m-%d').date()
                        elif isinstance(date_val, pd.Timestamp) or isinstance(date_val, datetime):
                            # If it's already a datetime object
                            date_obj = date_val.date() if hasattr(date_val, 'date') else date_val
                        else:
                            return False
                            
                        return date_obj.day == day and date_obj.month == month
                    except (ValueError, AttributeError, TypeError):
                        return False
                
                # Apply the filter
                filtered_df = df[df['Date'].apply(match_date)]
                
                if filtered_df.empty:
                    return jsonify({'message': 'No entries found for this date'}), 404
                    
                df = filtered_df
            except ValueError:
                return jsonify({'message': 'Invalid date format. Use DD-MM format.'}), 400
        
        # Convert DataFrame to list of dictionaries with correct field mapping
        entries = []
        for _, row in df.iterrows():
            entry = {
                'English Date': row.get('English Title', ''),
                'Hindi Date': row.get('Hindi Title', ''),
                'English Description': row.get('English Description', ''),
                'Hindi Description': row.get('Hindi Description', ''),
                'Image Path': row.get('Image Path', '')
            }
            entries.append(entry)
            
        return jsonify(entries), 200
        
    except Exception as e:
        return jsonify({'message': 'API Failed', 'error': str(e)}), 400

