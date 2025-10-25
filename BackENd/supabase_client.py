"""
Supabase client for fetching crew availability, network activity, and patches data.
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models import NetworkLoad, CrewMember, Patch

# For now, we'll use sample data structure that matches Supabase
# Install: pip install supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Supabase not installed. Using fallback sample data.")

class SupabaseDataFetcher:
    def __init__(self):
        self.client = None
        if SUPABASE_AVAILABLE:
            # Get credentials from environment variables
            supabase_url = os.getenv('SUPABASE_URL', '')
            supabase_key = os.getenv('SUPABASE_KEY', '')
            
            if supabase_url and supabase_key:
                try:
                    self.client = create_client(supabase_url, supabase_key)
                    print("Supabase client initialized successfully")
                except Exception as e:
                    print(f"Failed to initialize Supabase client: {e}")
                    self.client = None
            else:
                print("Supabase credentials not found in environment variables")
    
    def fetch_network_loads(self) -> List[NetworkLoad]:
        """
        Fetch network load predictions from Supabase.
        Expected table: network_loads
        Columns: id, day_of_week, day_number, hour, load_kilowatts, timestamp
        """
        if self.client:
            try:
                response = self.client.table('network_loads').select('*').execute()
                network_loads = []
                for row in response.data:
                    network_loads.append(NetworkLoad(
                        day_of_week=row['day_of_week'],
                        day_number=row['day_number'],
                        hour=row['hour'],
                        load_kilowatts=row['load_kilowatts']
                    ))
                print(f"Fetched {len(network_loads)} network load records from Supabase")
                return network_loads
            except Exception as e:
                print(f"Error fetching network loads from Supabase: {e}")
                return self._generate_fallback_network_loads()
        else:
            return self._generate_fallback_network_loads()
    
    def fetch_crew_members(self) -> List[CrewMember]:
        """
        Fetch crew availability from Supabase.
        Expected table: crew_members
        Columns: id, name, role, available_hours (JSON array of [start, end] pairs), skills (JSON array)
        """
        if self.client:
            try:
                response = self.client.table('crew_members').select('*').execute()
                crew_members = []
                for row in response.data:
                    crew_members.append(CrewMember(
                        id=row['id'],
                        name=row['name'],
                        role=row['role'],
                        available_hours=row['available_hours'],
                        skills=row.get('skills', [])
                    ))
                print(f"Fetched {len(crew_members)} crew members from Supabase")
                return crew_members
            except Exception as e:
                print(f"Error fetching crew members from Supabase: {e}")
                return self._generate_fallback_crew()
        else:
            return self._generate_fallback_crew()
    
    def fetch_patches(self) -> List[Patch]:
        """
        Fetch patches from Supabase.
        Expected table: patches
        Columns: id, name, duration, priority, min_crew, status, notes, is_urgent
        """
        if self.client:
            try:
                response = self.client.table('patches').select('*').execute()
                patches = []
                for row in response.data:
                    patches.append(Patch(
                        id=row['id'],
                        name=row['name'],
                        duration=row['duration'],
                        priority=row['priority'],
                        min_crew=row['min_crew'],
                        status=row.get('status', 'pending'),
                        notes=row.get('notes', ''),
                        is_urgent=row.get('is_urgent', False)
                    ))
                print(f"Fetched {len(patches)} patches from Supabase")
                return patches
            except Exception as e:
                print(f"Error fetching patches from Supabase: {e}")
                return self._generate_fallback_patches()
        else:
            return self._generate_fallback_patches()
    
    def add_patch(self, patch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new patch to Supabase"""
        if self.client:
            try:
                response = self.client.table('patches').insert(patch_data).execute()
                print(f"Added patch to Supabase: {patch_data['name']}")
                return response.data[0] if response.data else patch_data
            except Exception as e:
                print(f"Error adding patch to Supabase: {e}")
                return patch_data
        else:
            return patch_data
    
    def update_patch(self, patch_id: int, updates: Dict[str, Any]) -> bool:
        """Update a patch in Supabase"""
        if self.client:
            try:
                self.client.table('patches').update(updates).eq('id', patch_id).execute()
                print(f"Updated patch {patch_id} in Supabase")
                return True
            except Exception as e:
                print(f"Error updating patch in Supabase: {e}")
                return False
        else:
            return False
    
    # Fallback methods for when Supabase is not available
    def _generate_fallback_network_loads(self) -> List[NetworkLoad]:
        """Generate sample network loads when Supabase is unavailable"""
        import random
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        loads = []
        
        for day_num, day_name in enumerate(days):
            for hour in range(24):
                # Simulate realistic patterns
                base_load = 30
                
                # Weekend reduction
                if day_num >= 5:
                    base_load -= 15
                
                # Time of day variation
                if 9 <= hour <= 17:  # Business hours
                    base_load += 35
                elif 0 <= hour <= 6:  # Night hours
                    base_load -= 10
                
                # Add some randomness
                load = base_load + random.randint(-5, 15)
                load = max(5, min(85, load))
                
                loads.append(NetworkLoad(
                    day_of_week=day_name,
                    day_number=day_num,
                    hour=hour,
                    load_kilowatts=load
                ))
        
        return loads
    
    def _generate_fallback_crew(self) -> List[CrewMember]:
        """Generate sample crew when Supabase is unavailable"""
        return [
            CrewMember(id=1, name="Alex Chen", role="Senior Engineer", 
                      available_hours=[(8, 16), (18, 22)], skills=["Security", "Database"]),
            CrewMember(id=2, name="Sarah Miller", role="Systems Admin", 
                      available_hours=[(9, 17)], skills=["Networking", "Cloud"]),
            CrewMember(id=3, name="Mike Johnson", role="DevOps Engineer", 
                      available_hours=[(10, 18)], skills=["Automation", "Security"]),
            CrewMember(id=4, name="Emily Davis", role="Network Specialist", 
                      available_hours=[(7, 15), (20, 23)], skills=["Networking", "Monitoring"]),
            CrewMember(id=5, name="David Wilson", role="Security Analyst", 
                      available_hours=[(13, 21)], skills=["Security", "Compliance"])
        ]
    
    def _generate_fallback_patches(self) -> List[Patch]:
        """Generate sample patches when Supabase is unavailable"""
        return [
            Patch(id=1, name="Security Update CVE-2024", duration=3, priority=5, 
                  min_crew=2, status="pending", is_urgent=True),
            Patch(id=2, name="Database Migration", duration=4, priority=4, 
                  min_crew=3, status="pending", is_urgent=False),
            Patch(id=3, name="API Gateway Update", duration=2, priority=3, 
                  min_crew=2, status="pending", is_urgent=False),
            Patch(id=4, name="Monitoring System Upgrade", duration=2, priority=3, 
                  min_crew=1, status="pending", is_urgent=False),
            Patch(id=5, name="Load Balancer Config", duration=1, priority=2, 
                  min_crew=1, status="pending", is_urgent=False)
        ]

# Global instance
supabase_fetcher = SupabaseDataFetcher()

