"""
Community Reports Database
SQLite backend for citizen flood observations
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random
import json


class CommunityDatabase:
    """
    Manages citizen flood reports in SQLite database.
    """
    
    def __init__(self, db_path: str = "data/community_reports.db"):
        """Initialize database connection"""
        self.db_path = db_path
        
        # Create data directory if needed
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                reporter_name TEXT NOT NULL,
                location_name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                report_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                water_level_cm REAL,
                photo_url TEXT,
                verified INTEGER DEFAULT 0,
                upvotes INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_report(
        self,
        reporter_name: str,
        location_name: str,
        latitude: float,
        longitude: float,
        report_type: str,
        severity: str,
        description: str = "",
        water_level_cm: Optional[float] = None,
        photo_url: Optional[str] = None
    ) -> int:
        """
        Add a new citizen report.
        
        Returns:
        --------
        report_id : int
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO reports (
                timestamp, reporter_name, location_name, latitude, longitude,
                report_type, severity, description, water_level_cm, photo_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp, reporter_name, location_name, latitude, longitude,
            report_type, severity, description, water_level_cm, photo_url
        ))
        
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return report_id
    
    def get_all_reports(self, limit: int = 100) -> List[Dict]:
        """Get all reports (most recent first)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM reports
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        reports = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return reports
    
    def get_recent_reports(self, hours: int = 24) -> List[Dict]:
        """Get reports from last N hours"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            SELECT * FROM reports
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        ''', (cutoff_time,))
        
        columns = [desc[0] for desc in cursor.description]
        reports = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return reports
    
    def get_reports_by_severity(self, severity: str) -> List[Dict]:
        """Get reports filtered by severity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM reports
            WHERE severity = ?
            ORDER BY timestamp DESC
        ''', (severity,))
        
        columns = [desc[0] for desc in cursor.description]
        reports = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return reports
    
    def verify_report(self, report_id: int):
        """Mark a report as verified by authorities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE reports
            SET verified = 1
            WHERE id = ?
        ''', (report_id,))
        
        conn.commit()
        conn.close()
    
    def upvote_report(self, report_id: int):
        """Add an upvote to a report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE reports
            SET upvotes = upvotes + 1
            WHERE id = ?
        ''', (report_id,))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total reports
        cursor.execute('SELECT COUNT(*) FROM reports')
        total_reports = cursor.fetchone()[0]
        
        # Reports by severity
        cursor.execute('''
            SELECT severity, COUNT(*) as count
            FROM reports
            GROUP BY severity
        ''')
        by_severity = dict(cursor.fetchall())
        
        # Reports by type
        cursor.execute('''
            SELECT report_type, COUNT(*) as count
            FROM reports
            GROUP BY report_type
        ''')
        by_type = dict(cursor.fetchall())
        
        # Verified vs unverified
        cursor.execute('SELECT COUNT(*) FROM reports WHERE verified = 1')
        verified = cursor.fetchone()[0]
        
        # Last 24 hours
        cutoff = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('SELECT COUNT(*) FROM reports WHERE timestamp >= ?', (cutoff,))
        last_24h = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_reports': total_reports,
            'by_severity': by_severity,
            'by_type': by_type,
            'verified_count': verified,
            'unverified_count': total_reports - verified,
            'last_24h': last_24h
        }
    
    def populate_demo_data(self, count: int = 100):
        """
        Populate database with demo data for hackathon presentation.
        Only runs if database is empty.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if already populated
        cursor.execute('SELECT COUNT(*) FROM reports')
        existing = cursor.fetchone()[0]
        
        if existing > 0:
            print(f"Database already has {existing} reports. Skipping demo data.")
            conn.close()
            return
        
        print(f"Populating database with {count} demo reports...")
        
        # Demo data templates
        report_types = [
            'Flooding', 'Rising Water', 'Blocked Drain', 'Erosion',
            'Water Contamination', 'Infrastructure Damage', 'Wildlife Alert'
        ]
        
        severities = ['LOW', 'MODERATE', 'HIGH', 'CRITICAL']
        
        locations_ganga = [
            {'name': 'Haridwar Ghat', 'lat': 29.9457, 'lon': 78.1642},
            {'name': 'Rishikesh Bridge', 'lat': 30.0869, 'lon': 78.2676},
            {'name': 'Devprayag Confluence', 'lat': 30.1461, 'lon': 78.5989},
            {'name': 'Uttarkashi Town', 'lat': 30.7268, 'lon': 78.4354},
            {'name': 'Gangotri Temple', 'lat': 30.9993, 'lon': 78.9408},
            {'name': 'Tehri Dam Area', 'lat': 30.3753, 'lon': 78.4809},
            {'name': 'Kanpur Riverbank', 'lat': 26.4499, 'lon': 80.3319},
            {'name': 'Allahabad Sangam', 'lat': 25.4358, 'lon': 81.8463},
            {'name': 'Varanasi Ghats', 'lat': 25.3176, 'lon': 82.9739},
            {'name': 'Patna Riverside', 'lat': 25.5941, 'lon': 85.1376}
        ]
        
        descriptions_templates = {
            'Flooding': [
                'Water level rising rapidly in residential area',
                'Streets flooded, vehicles stuck',
                'Low-lying areas completely submerged',
                'Flash flood from upstream'
            ],
            'Rising Water': [
                'River level increasing steadily',
                'Water approaching danger mark',
                'Overflow from canal observed',
                'Tributaries swelling after rainfall'
            ],
            'Blocked Drain': [
                'Drainage system clogged with debris',
                'Manhole overflowing on main road',
                'Waterlogging due to blocked outlet',
                'Need urgent drain cleaning'
            ],
            'Erosion': [
                'Riverbank erosion threatening homes',
                'Soil collapse near embankment',
                'Agricultural land being washed away',
                'Retaining wall damaged'
            ],
            'Water Contamination': [
                'Unusual color in river water',
                'Dead fish observed downstream',
                'Foul smell from water body',
                'Suspected sewage mixing'
            ],
            'Infrastructure Damage': [
                'Bridge support pillar cracked',
                'Road washed away by current',
                'Embankment breach detected',
                'Flood protection wall damaged'
            ],
            'Wildlife Alert': [
                'Crocodile spotted near village',
                'Birds abandoning nesting area',
                'Unusual animal behavior observed',
                'Fish migration pattern changed'
            ]
        }
        
        reporter_names = [
            'Rajesh Kumar', 'Priya Sharma', 'Amit Singh', 'Neha Verma',
            'Rahul Gupta', 'Pooja Patel', 'Vikram Mehta', 'Anjali Rao',
            'Suresh Reddy', 'Kavita Desai', 'Manoj Joshi', 'Ritu Agarwal',
            'Deepak Yadav', 'Sunita Nair', 'Arjun Malhotra', 'Geeta Iyer'
        ]
        
        # Generate reports over last 7 days
        base_time = datetime.now()
        
        for i in range(count):
            # Random time in last 7 days (more recent = higher probability)
            hours_ago = random.choices(
                range(0, 168),  # 7 days = 168 hours
                weights=[100 - (h // 2) for h in range(168)],  # Higher weight for recent
                k=1
            )[0]
            
            timestamp = (base_time - timedelta(hours=hours_ago)).strftime('%Y-%m-%d %H:%M:%S')
            
            reporter = random.choice(reporter_names)
            location = random.choice(locations_ganga)
            
            # Add slight random variation to coordinates
            lat = location['lat'] + random.uniform(-0.01, 0.01)
            lon = location['lon'] + random.uniform(-0.01, 0.01)
            
            report_type = random.choice(report_types)
            
            # Severity distribution (more LOW/MODERATE than CRITICAL)
            severity = random.choices(
                severities,
                weights=[40, 35, 20, 5],
                k=1
            )[0]
            
            description = random.choice(descriptions_templates[report_type])
            
            # Water level for flooding reports
            water_level = None
            if report_type in ['Flooding', 'Rising Water']:
                water_level = random.uniform(20, 250)
            
            # Random verification (30% verified)
            verified = 1 if random.random() < 0.3 else 0
            
            # Random upvotes (0-50)
            upvotes = random.randint(0, 50)
            
            cursor.execute('''
                INSERT INTO reports (
                    timestamp, reporter_name, location_name, latitude, longitude,
                    report_type, severity, description, water_level_cm,
                    verified, upvotes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, reporter, location['name'], lat, lon,
                report_type, severity, description, water_level,
                verified, upvotes
            ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Successfully added {count} demo reports!")


if __name__ == "__main__":
    # Test the database
    print("🗄️ Community Database Test\n")
    
    db = CommunityDatabase()
    
    # Populate demo data
    db.populate_demo_data(count=100)
    
    # Get statistics
    stats = db.get_statistics()
    print(f"\nDatabase Statistics:")
    print(f"  Total Reports: {stats['total_reports']}")
    print(f"  Last 24h: {stats['last_24h']}")
    print(f"  Verified: {stats['verified_count']}")
    print(f"  By Severity: {stats['by_severity']}")
    print(f"  By Type: {stats['by_type']}")
    
    # Get recent reports
    recent = db.get_recent_reports(hours=24)
    print(f"\nRecent Reports (last 24h): {len(recent)}")
    for r in recent[:3]:
        print(f"  - {r['timestamp']}: {r['report_type']} at {r['location_name']} ({r['severity']})")
