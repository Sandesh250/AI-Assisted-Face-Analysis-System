"""
Quick script to index ALL faces in the sample_faces directory.
No internet required - uses existing images or creates synthetic ones.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_synthetic_faces(data_dir: Path, num_faces: int = 20) -> int:
    """Create synthetic colored faces for testing the system."""
    from PIL import Image, ImageDraw
    import random
    
    sample_faces_dir = data_dir / "sample_faces"
    sample_faces_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if there are already real images
    existing = list(sample_faces_dir.glob("*.jpg")) + list(sample_faces_dir.glob("*.png")) + list(sample_faces_dir.glob("*.jpeg"))
    if len(existing) > 0:
        print(f"[IMG] Found {len(existing)} existing images in {sample_faces_dir}")
        print("   Skipping synthetic face creation - will use existing images")
        return len(existing)
    
    # Sample names for demo
    names = [
        "John Smith", "Jane Doe", "Alex Johnson", "Maria Garcia",
        "David Brown", "Sarah Wilson", "Michael Lee", "Emily Davis",
        "Robert Taylor", "Lisa Anderson", "James Martin", "Jennifer White",
        "William Harris", "Amanda Clark", "Christopher Lewis", "Michelle Walker",
        "Daniel Hall", "Stephanie Allen", "Matthew Young", "Ashley King"
    ]
    
    print(f"[GEN] No existing images found. Creating {num_faces} synthetic sample faces...")
    
    for i in range(num_faces):
        img = Image.new('RGB', (200, 200))
        draw = ImageDraw.Draw(img)
        
        bg_color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        draw.rectangle([0, 0, 200, 200], fill=bg_color)
        
        face_color = (random.randint(200, 255), random.randint(180, 220), random.randint(150, 200))
        draw.ellipse([40, 30, 160, 180], fill=face_color)
        
        draw.ellipse([65, 70, 85, 90], fill='white')
        draw.ellipse([115, 70, 135, 90], fill='white')
        draw.ellipse([72, 77, 78, 83], fill='black')
        draw.ellipse([122, 77, 128, 83], fill='black')
        
        draw.arc([75, 110, 125, 150], 0, 180, fill='darkred', width=2)
        
        name = names[i % len(names)]
        filename = f"{name.replace(' ', '_')}_{i:04d}.jpg"
        img.save(sample_faces_dir / filename, quality=95)
    
    print(f"[OK] Created {num_faces} synthetic faces")
    return num_faces


def build_face_index(data_dir: Path) -> int:
    """Build FAISS index from ALL faces in sample_faces directory."""
    import asyncio
    from app.services.face_embeddings import face_embedding_service
    
    sample_faces_dir = data_dir / "sample_faces"
    
    # Get ALL images (jpg, jpeg, png)
    images = list(sample_faces_dir.glob("*.jpg")) + \
             list(sample_faces_dir.glob("*.jpeg")) + \
             list(sample_faces_dir.glob("*.png"))
    images = sorted(images)
    
    if not images:
        print("[ERR] No images found in sample_faces directory!")
        return 0
    
    print(f"\n[BUILD] Building face embedding index for {len(images)} images...")
    
    async def add_faces():
        count = 0
        
        for i, image_path in enumerate(images):
            # Extract name from filename
            name = image_path.stem.replace("_", " ").rsplit(" ", 1)[0].title()
            if not name:
                name = f"Person {i}"
            
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            success = await face_embedding_service.add_to_database(
                image_data=image_data,
                face_id=f"face_{i:04d}",
                name=name,
                image_path=str(image_path)
            )
            
            if success:
                count += 1
            
            if (i + 1) % 10 == 0 or (i + 1) == len(images):
                print(f"   Indexed {i + 1}/{len(images)} faces...")
        
        face_embedding_service.save_index()
        return count
    
    return asyncio.run(add_faces())


def clear_old_index(data_dir: Path) -> None:
    """Clear old FAISS index before rebuilding."""
    embeddings_dir = data_dir / "embeddings"
    faiss_file = embeddings_dir / "face_index.faiss"
    json_file = embeddings_dir / "face_index.json"
    
    if faiss_file.exists():
        faiss_file.unlink()
        print("[X] Removed old FAISS index")
    if json_file.exists():
        json_file.unlink()
        print("[X] Removed old metadata file")


def main():
    """Main entry point."""
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Face Database Builder")
    print("=" * 60)
    print()
    
    # Clear old index
    clear_old_index(data_dir)
    
    # Check for existing images or create synthetic ones
    num_images = create_synthetic_faces(data_dir, num_faces=20)
    
    # Build index for ALL images
    count = build_face_index(data_dir)
    
    print("\n" + "=" * 60)
    print(f"[OK] Done! Face database now has {count} faces indexed.")
    print("   Restart the backend and try Face Search!")
    print("=" * 60)


if __name__ == "__main__":
    main()
