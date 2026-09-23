#!/usr/bin/env python3
"""
Data Import Utility for Aircraft Maintenance Analytics System

This script imports sample data from CSV/JSON files into the database.
"""

import os
import sys
import csv
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Aircraft, Component, MaintenanceRecord, Alert, FlightData


def import_aircraft(csv_file):
    """Import aircraft from CSV file."""
    count = 0
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing = Aircraft.query.filter_by(registration_number=row['registration_number']).first()
            if existing:
                continue
                
            aircraft = Aircraft(
                registration_number=row['registration_number'],
                aircraft_type=row['aircraft_type'],
                model=row['model'],
                manufacturer=row['manufacturer'],
                year_manufactured=int(row['year_manufactured']) if row.get('year_manufactured') else None,
                total_flight_hours=float(row['total_flight_hours']) if row.get('total_flight_hours') else 0,
                total_cycles=int(row['total_cycles']) if row.get('total_cycles') else 0,
                status=row.get('status', 'active')
            )
            db.session.add(aircraft)
            count += 1
    
    db.session.commit()
    return count


def import_components(csv_file):
    """Import components from CSV file."""
    count = 0
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing = Component.query.filter_by(serial_number=row['serial_number']).first()
            if existing:
                continue
                
            component = Component(
                aircraft_id=int(row['aircraft_id']),
                part_number=row['part_number'],
                serial_number=row['serial_number'],
                component_type=row['component_type'],
                description=row.get('description', ''),
                installation_date=datetime.strptime(row['installation_date'], '%Y-%m-%d') if row.get('installation_date') else None,
                current_hours=float(row['current_hours']) if row.get('current_hours') else 0,
                current_cycles=int(row['current_cycles']) if row.get('current_cycles') else 0,
                max_hours=float(row['max_hours']) if row.get('max_hours') else None,
                max_cycles=int(row['max_cycles']) if row.get('max_cycles') else None,
                status=row.get('status', 'serviceable')
            )
            db.session.add(component)
            count += 1
    
    db.session.commit()
    return count


def import_maintenance(csv_file):
    """Import maintenance records from CSV file."""
    count = 0
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = MaintenanceRecord(
                aircraft_id=int(row['aircraft_id']),
                component_id=int(row['component_id']) if row.get('component_id') and row['component_id'] else None,
                maintenance_type=row['maintenance_type'],
                description=row.get('description', ''),
                work_order_number=row.get('work_order_number'),
                performed_by=row.get('performed_by'),
                scheduled_date=datetime.strptime(row['scheduled_date'], '%Y-%m-%d') if row.get('scheduled_date') else None,
                completed_date=datetime.strptime(row['completed_date'], '%Y-%m-%d') if row.get('completed_date') else None,
                labor_hours=float(row['labor_hours']) if row.get('labor_hours') else None,
                parts_cost=float(row['parts_cost']) if row.get('parts_cost') else None,
                labor_cost=float(row['labor_cost']) if row.get('labor_cost') else None,
                total_cost=float(row['total_cost']) if row.get('total_cost') else None,
                status=row.get('status', 'scheduled'),
                priority=row.get('priority', 'medium'),
                notes=row.get('notes')
            )
            db.session.add(record)
            count += 1
    
    db.session.commit()
    return count


def import_flight_data(csv_file):
    """Import flight data from CSV file."""
    count = 0
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            flight = FlightData(
                aircraft_id=int(row['aircraft_id']),
                flight_date=datetime.strptime(row['flight_date'], '%Y-%m-%d'),
                flight_number=row.get('flight_number'),
                origin=row.get('origin'),
                destination=row.get('destination'),
                flight_hours=float(row['flight_hours']) if row.get('flight_hours') else None,
                flight_cycles=int(row['flight_cycles']) if row.get('flight_cycles') else 1,
                takeoffs=int(row['takeoffs']) if row.get('takeoffs') else 1,
                landings=int(row['landings']) if row.get('landings') else 1,
                fuel_burned=float(row['fuel_burned']) if row.get('fuel_burned') else None,
                notes=row.get('notes')
            )
            db.session.add(flight)
            count += 1
    
    db.session.commit()
    return count


def import_alerts(json_file):
    """Import alerts from JSON file."""
    count = 0
    with open(json_file, 'r') as f:
        alerts_data = json.load(f)
        
    for alert_data in alerts_data:
        alert = Alert(
            aircraft_id=int(alert_data['aircraft_id']),
            component_id=int(alert_data['component_id']) if alert_data.get('component_id') else None,
            alert_type=alert_data['type'],
            title=alert_data['title'],
            message=alert_data.get('message', ''),
            severity=alert_data.get('severity', 'medium'),
            due_date=datetime.strptime(alert_data['due_date'], '%Y-%m-%d') if alert_data.get('due_date') else None
        )
        db.session.add(alert)
        count += 1
    
    db.session.commit()
    return count


def main():
    app = create_app('development')
    
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    with app.app_context():
        print('Importing data from CSV/JSON files...')
        print()
        
        aircraft_csv = os.path.join(data_dir, 'aircraft.csv')
        if os.path.exists(aircraft_csv):
            count = import_aircraft(aircraft_csv)
            print(f'Imported {count} aircraft')
        
        components_csv = os.path.join(data_dir, 'components.csv')
        if os.path.exists(components_csv):
            count = import_components(components_csv)
            print(f'Imported {count} components')
        
        maintenance_csv = os.path.join(data_dir, 'maintenance_records.csv')
        if os.path.exists(maintenance_csv):
            count = import_maintenance(maintenance_csv)
            print(f'Imported {count} maintenance records')
        
        flight_csv = os.path.join(data_dir, 'flight_data.csv')
        if os.path.exists(flight_csv):
            count = import_flight_data(flight_csv)
            print(f'Imported {count} flight records')
        
        alerts_json = os.path.join(data_dir, 'alerts.json')
        if os.path.exists(alerts_json):
            count = import_alerts(alerts_json)
            print(f'Imported {count} alerts')
        
        print()
        print('Import complete!')
        print()
        print('Current database contents:')
        print(f'  Aircraft: {Aircraft.query.count()}')
        print(f'  Components: {Component.query.count()}')
        print(f'  Maintenance Records: {MaintenanceRecord.query.count()}')
        print(f'  Flight Data: {FlightData.query.count()}')
        print(f'  Alerts: {Alert.query.count()}')


if __name__ == '__main__':
    main()
