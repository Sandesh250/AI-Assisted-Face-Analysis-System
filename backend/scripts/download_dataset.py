"""
Script to download and prepare the LFW (Labeled Faces in the Wild) dataset.
This dataset is public and suitable for educational purposes.
Uses scikit-learn's built-in downloader with reliable mirrors.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def download_lfw_sklearn(data_dir: Path, max_images: int = 100) -> None:
    """
    Download LFW dataset using scikit-learn (more reliable mirrors).
    
    Args:
        data_dir: Directory to store images
        max_images: Maximum number of images to use
    """
    try:
        from sklearn.datasets import fetch_lfw_people
        from PIL import Image
        import numpy as np
    except ImportError:
        print("❌ Missing dependencies. Installing...")
        os.system(f"{sys.executable} -m pip install scikit-learn pillow")
        from sklearn.datasets import fetch_lfw_people
        from PIL import Image
        import numpy as np
    
    sample_faces_dir = data_dir / "sample_faces"
    sample_faces_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if already downloaded
    existing = list(sample_faces_dir.glob("*.jpg"))
    if len(existing) >= max_images:
        print(f"✅ Sample faces already exist in {sample_faces_dir}")
        print(f"   Found {len(existing)} images")
        return
    
    print("📥 Downloading LFW Dataset via scikit-learn...")
    print("   This uses reliable mirrors and caches the download.")
    print()
    
    # Fetch LFW data - this downloads from reliable sklearn mirrors
    lfw = fetch_lfw_people(
        min_faces_per_person=1,
        resize=1.0,
        download_if_missing=True
    )
    
    print(f"   Found {len(lfw.images)} face images")
    
    # Save selected images
    print(f"\n📁 Saving {max_images} sample images...")
    
    count = 0
    for i in range(min(max_images, len(lfw.images))):
        # Get image and name
        img_array = lfw.images[i]
        name = lfw.target_names[lfw.target[i]] if lfw.target[i] < len(lfw.target_names) else f"Person_{i}"
        
        # Convert to PIL Image (LFW images are already uint8 0-255)
        img = Image.fromarray(img_array.astype(np.uint8))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save
        filename = f"{name.replace(' ', '_')}_{i:04d}.jpg"
        img.save(sample_faces_dir / filename, quality=95)
        count += 1
        
        if (i + 1) % 20 == 0:
            print(f"   Saved {i + 1}/{max_images} images...")
    
    print(f"\n✅ Saved {count} sample images to {sample_faces_dir}")


def create_sample_metadata(data_dir: Path) -> None:
    """Create metadata file for sample faces."""
    import json
    
    sample_faces_dir = data_dir / "sample_faces"
    metadata = []
    
    for i, image_path in enumerate(sorted(sample_faces_dir.glob("*.jpg"))):
        # Extract name from filename
        name = image_path.stem.replace("_", " ").rsplit(" ", 1)[0].title()
        
        metadata.append({
            "id": f"face_{i:04d}",
            "name": name,
            "filename": image_path.name,
            "path": str(image_path)
        })
    
    metadata_path = data_dir / "sample_faces_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Created metadata file: {metadata_path}")
    print(f"   Total faces: {len(metadata)}")


def build_face_index(data_dir: Path) -> None:
    """Build FAISS index from sample faces."""
    import asyncio
    from app.services.face_embeddings import face_embedding_service
    
    sample_faces_dir = data_dir / "sample_faces"
    
    print("\n🔧 Building face embedding index...")
    print("   This may take a few minutes.")
    
    async def add_faces():
        count = 0
        images = list(sorted(sample_faces_dir.glob("*.jpg")))
        
        for i, image_path in enumerate(images):
            name = image_path.stem.replace("_", " ").rsplit(" ", 1)[0].title()
            
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
            
            if (i + 1) % 10 == 0:
                print(f"   Processed {i + 1}/{len(images)} images...")
        
        face_embedding_service.save_index()
        print(f"\n✅ Added {count} faces to the FAISS index")
    
    asyncio.run(add_faces())


def main():
    """Main entry point."""
    # Get data directory
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("LFW Dataset Downloader for Educational AI Project")
    print("=" * 60)
    print()
    print("⚠️  EDUCATIONAL USE ONLY")
    print("   This dataset is for learning and research purposes.")
    print("   The LFW dataset contains public figures' photos.")
    print()
    
    # Download dataset using sklearn (reliable mirrors)
    download_lfw_sklearn(data_dir, max_images=100)
    
    # Create metadata
    create_sample_metadata(data_dir)
    
    # Build index
    print("\n🔧 Building face embedding index...")
    build_face_index(data_dir)
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("   Face database is now populated and ready for searching.")
    print("=" * 60)


if __name__ == "__main__":
    main()
