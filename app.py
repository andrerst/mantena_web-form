from flask import Flask, render_template, request, redirect, url_for
import os
import json
import datetime

app = Flask(__name__)

SAVE_DIR = 'saved_forms'
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

@app.route('/', methods=['GET', 'POST'])
def form_page():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        # Handle checkboxes: convert 'on' to True, absent to False
        checkbox_fields = [
            'reason_death', 'reason_custody_removed', 'reason_mentally_physically_unable',
            'reason_not_involved', 'reason_unknown_whereabouts', 'reason_unable_to_reach',
            'activate_execution', 'activate_incapacitated', 'activate_debilitated',
            'activate_detained_immigration', 'activate_incarcerated', 'activate_deployed_military',
            'activate_upon_death', 'activate_other'
        ]
        for field in checkbox_fields:
            form_data[field] = field in form_data  # True if checked, else False
        
        # Generate filename: use child_name if provided, else timestamp
        child_name = form_data.get('child_name', '').replace(' ', '_')[:20] or 'unknown'
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"poa_{child_name}_{timestamp}.json"
        filepath = os.path.join(SAVE_DIR, filename)
        
        with open(filepath, 'w') as f:
            json.dump(form_data, f, indent=4)
        
        return redirect(url_for('success', filename=filename))
    
    else:
        # This is implicit for GET, but adding for clarity
        today = datetime.date.today()  # Gets current date (e.g., 2026-01-17) server's local time. For UTC: datetime.datetime.utcnow().date(), for timezones, use pytz
        today_month = today.strftime('%B')  # Full month name: 'January'
        today_day = today.day  # Integer: 17
        today_year = today.strftime('%y')  # Two-digit year: '26'
        
        return render_template('form.html',
                                today_month=today_month,
                                today_day=today_day,
                                today_year=today_year)
    
    # return render_template('form.html')

@app.route('/success/<filename>')
def success(filename):
    filepath = os.path.join(SAVE_DIR, filename)
    with open(filepath, 'r') as f:
        form_data = json.load(f)
    
    return render_template('printable.html', data=form_data, filename=filename)

# Office dashboard to list saved forms
@app.route('/office')
def office():
    files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.json')]
    return render_template('office.html', files=files)

if __name__ == '__main__':
    app.run(debug=True)
