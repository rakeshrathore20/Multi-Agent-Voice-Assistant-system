"""
Knowledge Agent - Manages car inventory and provides search/filtering
"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class KnowledgeAgent:
    """Agent responsible for vehicle knowledge base management."""
    
    def __init__(self, knowledge_base_path: str):
        """Initialize the knowledge agent.
        
        Args:
            knowledge_base_path: Path to the JSON knowledge base file
        """
        self.knowledge_base_path = Path(knowledge_base_path)
        self.vehicles = []
        self._load_knowledge_base()
        
        logger.info(f"Knowledge Agent initialized with {len(self.vehicles)} vehicles")
    
    def _load_knowledge_base(self):
        """Load vehicle data from JSON file."""
        try:
            if not self.knowledge_base_path.exists():
                logger.warning(f"Knowledge base not found at {self.knowledge_base_path}")
                self._create_default_knowledge_base()
            
            with open(self.knowledge_base_path, 'r') as f:
                data = json.load(f)
                self.vehicles = data.get('vehicles', [])
                
            logger.info(f"Loaded {len(self.vehicles)} vehicles from knowledge base")
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
            self.vehicles = []
    
    def _create_default_knowledge_base(self):
        """Create a default knowledge base if none exists."""
        default_data = {
            "vehicles": [
                {
                    "id": "v001",
                    "make": "Toyota",
                    "model": "RAV4",
                    "year": 2024,
                    "type": "SUV",
                    "price": 32000,
                    "features": [
                        "All-Wheel Drive",
                        "Lane Departure Warning",
                        "Adaptive Cruise Control",
                        "Backup Camera"
                    ],
                    "specs": {
                        "engine": "2.5L 4-Cylinder",
                        "horsepower": 203,
                        "mpg": "28 city / 35 highway",
                        "seating": 5
                    },
                    "available": True
                },
                {
                    "id": "v002",
                    "make": "Honda",
                    "model": "CR-V",
                    "year": 2024,
                    "type": "SUV",
                    "price": 30500,
                    "features": [
                        "Spacious Interior",
                        "Honda Sensing Suite",
                        "Blind Spot Monitoring",
                        "Apple CarPlay"
                    ],
                    "specs": {
                        "engine": "1.5L Turbo",
                        "horsepower": 190,
                        "mpg": "27 city / 32 highway",
                        "seating": 5
                    },
                    "available": True
                },
                {
                    "id": "v003",
                    "make": "Ford",
                    "model": "Explorer",
                    "year": 2024,
                    "type": "SUV",
                    "price": 38000,
                    "features": [
                        "Third Row Seating",
                        "Twin-Turbo Engine",
                        "Advanced Safety Features",
                        "Panoramic Sunroof"
                    ],
                    "specs": {
                        "engine": "2.3L EcoBoost",
                        "horsepower": 300,
                        "mpg": "21 city / 28 highway",
                        "seating": 7
                    },
                    "available": True
                },
                {
                    "id": "v004",
                    "make": "Honda",
                    "model": "Accord",
                    "year": 2024,
                    "type": "SEDAN",
                    "price": 28500,
                    "features": [
                        "Hybrid Option",
                        "Advanced Safety Suite",
                        "Leather Interior",
                        "Wireless Charging"
                    ],
                    "specs": {
                        "engine": "1.5L Turbo",
                        "horsepower": 192,
                        "mpg": "30 city / 38 highway",
                        "seating": 5
                    },
                    "available": True
                },
                {
                    "id": "v005",
                    "make": "Toyota",
                    "model": "Camry",
                    "year": 2024,
                    "type": "SEDAN",
                    "price": 27000,
                    "features": [
                        "Toyota Safety Sense",
                        "Premium Audio System",
                        "Heated Seats",
                        "Dual-Zone Climate"
                    ],
                    "specs": {
                        "engine": "2.5L 4-Cylinder",
                        "horsepower": 203,
                        "mpg": "28 city / 39 highway",
                        "seating": 5
                    },
                    "available": True
                },
                {
                    "id": "v006",
                    "make": "Ford",
                    "model": "F-150",
                    "year": 2024,
                    "type": "TRUCK",
                    "price": 42000,
                    "features": [
                        "Towing Package",
                        "4WD",
                        "Crew Cab",
                        "Bed Liner"
                    ],
                    "specs": {
                        "engine": "3.5L V6",
                        "horsepower": 400,
                        "mpg": "20 city / 24 highway",
                        "seating": 5,
                        "towing_capacity": "13000 lbs"
                    },
                    "available": True
                },
                {
                    "id": "v007",
                    "make": "Chevrolet",
                    "model": "Silverado",
                    "year": 2024,
                    "type": "TRUCK",
                    "price": 40000,
                    "features": [
                        "High Country Package",
                        "Advanced Trailering",
                        "Bose Audio",
                        "Leather Interior"
                    ],
                    "specs": {
                        "engine": "5.3L V8",
                        "horsepower": 355,
                        "mpg": "17 city / 23 highway",
                        "seating": 6,
                        "towing_capacity": "11500 lbs"
                    },
                    "available": True
                },
                {
                    "id": "v008",
                    "make": "BMW",
                    "model": "3 Series",
                    "year": 2024,
                    "type": "SEDAN",
                    "price": 45000,
                    "features": [
                        "Luxury Package",
                        "Sport Suspension",
                        "Premium Sound",
                        "Navigation System"
                    ],
                    "specs": {
                        "engine": "2.0L Turbo",
                        "horsepower": 255,
                        "mpg": "26 city / 36 highway",
                        "seating": 5
                    },
                    "available": True
                }
            ]
        }
        
        # Create directory if it doesn't exist
        self.knowledge_base_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.knowledge_base_path, 'w') as f:
            json.dump(default_data, f, indent=2)
        
        self.vehicles = default_data['vehicles']
        logger.info(f"Created default knowledge base with {len(self.vehicles)} vehicles")
    
    def search_vehicles(
        self,
        vehicle_type: Optional[str] = None,
        make: Optional[str] = None,
        model: Optional[str] = None,
        max_price: Optional[int] = None,
        min_price: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for vehicles based on criteria.
        
        Args:
            vehicle_type: Type of vehicle (SUV, SEDAN, TRUCK, etc.)
            make: Vehicle manufacturer
            model: Vehicle model
            max_price: Maximum price
            min_price: Minimum price
            
        Returns:
            List of matching vehicles
        """
        results = self.vehicles.copy()
        
        if vehicle_type:
            results = [
                v for v in results
                if v['type'].upper() == vehicle_type.upper()
            ]
        
        if make:
            results = [
                v for v in results
                if v['make'].lower() == make.lower()
            ]
        
        if model:
            results = [
                v for v in results
                if model.lower() in v['model'].lower()
            ]
        
        if max_price:
            results = [v for v in results if v['price'] <= max_price]
        
        if min_price:
            results = [v for v in results if v['price'] >= min_price]
        
        # Filter available vehicles
        results = [v for v in results if v.get('available', True)]
        
        logger.info(f"Search returned {len(results)} vehicles")
        return results
    
    def get_vehicle_by_id(self, vehicle_id: str) -> Optional[Dict[str, Any]]:
        """Get vehicle by ID.
        
        Args:
            vehicle_id: Vehicle identifier
            
        Returns:
            Vehicle dictionary or None if not found
        """
        for vehicle in self.vehicles:
            if vehicle['id'] == vehicle_id:
                return vehicle
        return None
    
    def get_vehicle_by_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get vehicle by model name.
        
        Args:
            model_name: Model name to search for
            
        Returns:
            Vehicle dictionary or None if not found
        """
        for vehicle in self.vehicles:
            if model_name.lower() in vehicle['model'].lower():
                return vehicle
        return None
    
    def get_all_vehicle_types(self) -> List[str]:
        """Get list of all available vehicle types.
        
        Returns:
            List of unique vehicle types
        """
        return list(set(v['type'] for v in self.vehicles))
    
    def get_vehicles_by_price_range(
        self,
        min_price: int,
        max_price: int
    ) -> List[Dict[str, Any]]:
        """Get vehicles within a price range.
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
            
        Returns:
            List of vehicles in the price range
        """
        return [
            v for v in self.vehicles
            if min_price <= v['price'] <= max_price and v.get('available', True)
        ]
    
    def get_featured_vehicles(self, count: int = 3) -> List[Dict[str, Any]]:
        """Get featured vehicles.
        
        Args:
            count: Number of featured vehicles to return
            
        Returns:
            List of featured vehicles
        """
        available = [v for v in self.vehicles if v.get('available', True)]
        return sorted(available, key=lambda x: x['price'], reverse=True)[:count]
    
    def update_vehicle_availability(
        self,
        vehicle_id: str,
        available: bool
    ) -> bool:
        """Update vehicle availability status.
        
        Args:
            vehicle_id: Vehicle identifier
            available: Availability status
            
        Returns:
            True if successful, False otherwise
        """
        for vehicle in self.vehicles:
            if vehicle['id'] == vehicle_id:
                vehicle['available'] = available
                self._save_knowledge_base()
                logger.info(f"Updated availability for vehicle {vehicle_id}")
                return True
        return False
    
    def _save_knowledge_base(self):
        """Save current vehicle data to JSON file."""
        try:
            with open(self.knowledge_base_path, 'w') as f:
                json.dump({'vehicles': self.vehicles}, f, indent=2)
            logger.info("Knowledge base saved successfully")
        except Exception as e:
            logger.error(f"Error saving knowledge base: {str(e)}")
