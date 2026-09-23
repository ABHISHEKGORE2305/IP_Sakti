// src/components/AyurvedicScene.jsx
// ─── Procedural 3D Ayurvedic apothecary scene ─────────────────
// Recreates the reference image: warm wooden table, amber bottles,
// herbal poultice bundles, brass hanging vessel, incense smoke,
// potted plants, mortar bowl, all in warm cinematic lighting.

import { useRef, useMemo, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import {
  Environment,
  Plane,
  MeshDistortMaterial,
  Float,
} from '@react-three/drei';
import * as THREE from 'three';

/* ── Utility: wood-like material ───────────────────────────── */
function WoodMaterial({ color = '#4a2e18', roughness = 0.85 }) {
  return (
    <meshStandardMaterial
      color={color}
      roughness={roughness}
      metalness={0.02}
    />
  );
}

/* ── Wooden Table ──────────────────────────────────────────── */
function Table() {
  return (
    <group position={[0, -1.25, 0]}>
      {/* Table top */}
      <mesh castShadow receiveShadow>
        <boxGeometry args={[6.5, 0.13, 3.2]} />
        <meshStandardMaterial color="#3d2410" roughness={0.78} metalness={0.02} />
      </mesh>
      {/* Table edge highlight (slightly lighter strip along front) */}
      <mesh position={[0, -0.04, 1.55]}>
        <boxGeometry args={[6.5, 0.05, 0.04]} />
        <meshStandardMaterial color="#5a3820" roughness={0.7} />
      </mesh>
      {/* Legs */}
      {[[-2.8, -0.9, -1.3], [2.8, -0.9, -1.3], [-2.8, -0.9, 1.3], [2.8, -0.9, 1.3]].map(
        ([x, y, z], i) => (
          <mesh key={i} position={[x, y, z]} castShadow>
            <cylinderGeometry args={[0.07, 0.07, 1.8, 8]} />
            <meshStandardMaterial color="#2e1a0e" roughness={0.85} />
          </mesh>
        )
      )}
    </group>
  );
}

/* ── Amber Glass Bottle ────────────────────────────────────── */
function AmberBottle({ position, scale = 1, variant = 'tall' }) {
  const configs = {
    tall:   { bodyH: 1.2, bodyR: 0.14, neckH: 0.55, neckR: 0.055 },
    medium: { bodyH: 0.85, bodyR: 0.16, neckH: 0.42, neckR: 0.06 },
    small:  { bodyH: 0.52, bodyR: 0.1,  neckH: 0.25, neckR: 0.045 },
  };
  const c = configs[variant];
  const amberMat = useMemo(
    () =>
      new THREE.MeshPhysicalMaterial({
        color: new THREE.Color('#7b3e0a'),
        roughness: 0.08,
        metalness: 0.05,
        transmission: 0.72,
        thickness: 0.6,
        ior: 1.5,
        transparent: true,
        opacity: 0.88,
      }),
    []
  );

  return (
    <Float speed={0.6} rotationIntensity={0.03} floatIntensity={0.08}>
      <group position={position} scale={scale}>
        {/* Body */}
        <mesh castShadow material={amberMat}>
          <cylinderGeometry args={[c.bodyR, c.bodyR * 0.92, c.bodyH, 20]} />
        </mesh>
        {/* Shoulder */}
        <mesh position={[0, c.bodyH / 2 + 0.08, 0]} material={amberMat}>
          <cylinderGeometry args={[c.neckR, c.bodyR * 0.9, 0.16, 20]} />
        </mesh>
        {/* Neck */}
        <mesh position={[0, c.bodyH / 2 + 0.08 + c.neckH / 2 + 0.06, 0]} material={amberMat}>
          <cylinderGeometry args={[c.neckR, c.neckR, c.neckH, 16]} />
        </mesh>
        {/* Cork stopper */}
        <mesh
          position={[0, c.bodyH / 2 + 0.08 + c.neckH + 0.14, 0]}
          castShadow
        >
          <cylinderGeometry args={[c.neckR + 0.01, c.neckR + 0.01, 0.1, 12]} />
          <meshStandardMaterial color="#8b6040" roughness={0.95} />
        </mesh>
      </group>
    </Float>
  );
}

/* ── Herbal Poultice Bundle ────────────────────────────────── */
function PoulticeBall({ position, scale = 1 }) {
  return (
    <Float speed={0.5} rotationIntensity={0.04} floatIntensity={0.07}>
      <group position={position} scale={scale}>
        {/* Main round ball */}
        <mesh castShadow>
          <sphereGeometry args={[0.26, 20, 20]} />
          <meshStandardMaterial color="#e8e0cc" roughness={0.95} metalness={0} />
        </mesh>
        {/* Wrap lines (torus rings) */}
        {[0, 30, 60, 90].map((deg, i) => (
          <mesh key={i} rotation={[0, 0, (deg * Math.PI) / 180]}>
            <torusGeometry args={[0.26, 0.012, 8, 32]} />
            <meshStandardMaterial color="#c8b898" roughness={0.9} />
          </mesh>
        ))}
        {/* Tied top knob */}
        <mesh position={[0, 0.3, 0]}>
          <cylinderGeometry args={[0.08, 0.04, 0.18, 12]} />
          <meshStandardMaterial color="#d8cdb8" roughness={0.95} />
        </mesh>
        {/* Green leaves peeking */}
        <mesh position={[0.22, 0.1, 0]} rotation={[0.2, 0.5, 0.3]}>
          <planeGeometry args={[0.18, 0.1]} />
          <meshStandardMaterial color="#4a7c3f" roughness={0.8} side={THREE.DoubleSide} />
        </mesh>
      </group>
    </Float>
  );
}

/* ── Wooden Tray ───────────────────────────────────────────── */
function WoodenTray({ position, size = [1.1, 0.06, 0.7] }) {
  return (
    <mesh position={position} receiveShadow>
      <boxGeometry args={size} />
      <meshStandardMaterial color="#5c3318" roughness={0.88} />
    </mesh>
  );
}

/* ── Stone Mortar ──────────────────────────────────────────── */
function Mortar({ position }) {
  return (
    <group position={position}>
      {/* Bowl body */}
      <mesh castShadow>
        <cylinderGeometry args={[0.22, 0.16, 0.22, 20, 1, true]} />
        <meshStandardMaterial color="#5a5550" roughness={0.9} metalness={0.05} />
      </mesh>
      {/* Bottom */}
      <mesh position={[0, -0.1, 0]}>
        <cylinderGeometry args={[0.16, 0.16, 0.02, 20]} />
        <meshStandardMaterial color="#5a5550" roughness={0.9} />
      </mesh>
      {/* Herb fill */}
      <mesh position={[0, 0.04, 0]}>
        <cylinderGeometry args={[0.18, 0.18, 0.06, 20]} />
        <meshStandardMaterial color="#3d6b2e" roughness={1} />
      </mesh>
      {/* Small plant leaves */}
      {[0, 90, 180].map((deg, i) => (
        <mesh
          key={i}
          position={[Math.sin((deg * Math.PI) / 180) * 0.15, 0.18, Math.cos((deg * Math.PI) / 180) * 0.15]}
          rotation={[0.3, (deg * Math.PI) / 180, 0.2]}
        >
          <planeGeometry args={[0.14, 0.22]} />
          <meshStandardMaterial color="#3a7030" roughness={0.8} side={THREE.DoubleSide} />
        </mesh>
      ))}
    </group>
  );
}

/* ── Herb Bowl with Incense ────────────────────────────────── */
function HerbBowl({ position }) {
  const smokeRef = useRef();
  useFrame(({ clock }) => {
    if (smokeRef.current) {
      smokeRef.current.children.forEach((p, i) => {
        p.position.y = ((clock.getElapsedTime() * 0.25 + i * 0.4) % 1.8) + 0.1;
        p.position.x = Math.sin(clock.getElapsedTime() * 0.4 + i) * 0.04;
        p.material.opacity = Math.max(0, 0.35 - p.position.y * 0.2);
      });
    }
  });

  const smokePuffs = useMemo(
    () =>
      Array.from({ length: 7 }, (_, i) => ({
        y: i * 0.26,
        x: Math.sin(i * 0.9) * 0.03,
      })),
    []
  );

  return (
    <group position={position}>
      {/* Bowl */}
      <mesh castShadow>
        <cylinderGeometry args={[0.24, 0.18, 0.2, 18, 1, true]} />
        <meshStandardMaterial color="#4a2e18" roughness={0.9} />
      </mesh>
      <mesh position={[0, -0.1, 0]}>
        <cylinderGeometry args={[0.18, 0.18, 0.02, 18]} />
        <meshStandardMaterial color="#4a2e18" roughness={0.9} />
      </mesh>
      {/* Herb fill */}
      <mesh position={[0, 0.02, 0]}>
        <cylinderGeometry args={[0.2, 0.2, 0.08, 18]} />
        <meshStandardMaterial color="#6b4020" roughness={1} />
      </mesh>

      {/* Incense stick */}
      <group position={[0.05, 0.05, 0.05]} rotation={[0, 0, -0.35]}>
        <mesh>
          <cylinderGeometry args={[0.005, 0.005, 0.55, 6]} />
          <meshStandardMaterial color="#8b5e3c" roughness={0.95} />
        </mesh>
        {/* Glowing ember tip */}
        <mesh position={[0, 0.28, 0]}>
          <sphereGeometry args={[0.012, 8, 8]} />
          <meshStandardMaterial color="#ff6b20" emissive="#ff4400" emissiveIntensity={2.5} />
        </mesh>

        {/* Smoke particles */}
        <group ref={smokeRef} position={[0, 0.3, 0]}>
          {smokePuffs.map((s, i) => (
            <mesh key={i} position={[s.x, s.y, 0]}>
              <sphereGeometry args={[0.018 + i * 0.006, 6, 6]} />
              <meshStandardMaterial
                color="#d4c8b8"
                transparent
                opacity={0.3 - i * 0.035}
                depthWrite={false}
              />
            </mesh>
          ))}
        </group>
      </group>
    </group>
  );
}

/* ── Small Spice Bowl ──────────────────────────────────────── */
function SpiceBowl({ position, powderColor = '#d4a020', size = 0.15 }) {
  return (
    <group position={position}>
      <mesh>
        <cylinderGeometry args={[size, size * 0.85, size * 0.6, 16, 1, true]} />
        <meshStandardMaterial color="#6a3e22" roughness={0.9} />
      </mesh>
      <mesh position={[0, -size * 0.28, 0]}>
        <cylinderGeometry args={[size * 0.85, size * 0.85, 0.015, 16]} />
        <meshStandardMaterial color="#6a3e22" roughness={0.9} />
      </mesh>
      {/* Powder fill */}
      <mesh position={[0, size * 0.05, 0]}>
        <cylinderGeometry args={[size * 0.88, size * 0.88, size * 0.22, 16]} />
        <meshStandardMaterial color={powderColor} roughness={1} />
      </mesh>
    </group>
  );
}

/* ── Cinnamon Stick ─────────────────────────────────────────── */
function CinnamonStick({ position, rotation = [0, 0, 0] }) {
  return (
    <mesh position={position} rotation={rotation} castShadow>
      <cylinderGeometry args={[0.025, 0.022, 0.45, 10]} />
      <meshStandardMaterial color="#8b4513" roughness={0.95} />
    </mesh>
  );
}

/* ── Potted Plant ──────────────────────────────────────────── */
function PottedPlant({ position, scale = 1, plantType = 'ficus' }) {
  const leavesData = useMemo(() => {
    const count = plantType === 'ficus' ? 8 : 14;
    return Array.from({ length: count }, (_, i) => {
      const angle = (i / count) * Math.PI * 2;
      const heightStep = plantType === 'ficus' ? i * 0.18 : i * 0.12;
      const radius = plantType === 'ficus' ? 0.35 + Math.random() * 0.2 : 0.25 + Math.random() * 0.15;
      return {
        x: Math.sin(angle) * radius,
        y: 0.5 + heightStep + Math.random() * 0.1,
        z: Math.cos(angle) * radius,
        rx: -0.3 + Math.random() * 0.6,
        ry: angle,
        rz: -0.2 + Math.random() * 0.4,
        w: plantType === 'ficus' ? 0.32 + Math.random() * 0.18 : 0.14 + Math.random() * 0.12,
        h: plantType === 'ficus' ? 0.42 + Math.random() * 0.18 : 0.22 + Math.random() * 0.12,
      };
    });
  }, [plantType]);

  const leafColor = plantType === 'ficus' ? '#2d5e28' : '#3a7535';

  return (
    <group position={position} scale={scale}>
      {/* Terracotta pot */}
      <mesh castShadow position={[0, 0, 0]}>
        <cylinderGeometry args={[0.28, 0.2, 0.46, 16]} />
        <meshStandardMaterial color="#8b4c30" roughness={0.88} />
      </mesh>
      {/* Pot rim */}
      <mesh position={[0, 0.25, 0]}>
        <torusGeometry args={[0.28, 0.03, 8, 20]} />
        <meshStandardMaterial color="#7a3f28" roughness={0.88} />
      </mesh>
      {/* Soil */}
      <mesh position={[0, 0.22, 0]}>
        <cylinderGeometry args={[0.26, 0.26, 0.04, 16]} />
        <meshStandardMaterial color="#3a2010" roughness={1} />
      </mesh>
      {/* Stem */}
      <mesh position={[0, 0.6, 0]} castShadow>
        <cylinderGeometry args={[0.025, 0.035, 0.7, 8]} />
        <meshStandardMaterial color="#4a3020" roughness={0.9} />
      </mesh>
      {/* Leaves */}
      {leavesData.map((leaf, i) => (
        <mesh
          key={i}
          position={[leaf.x, leaf.y, leaf.z]}
          rotation={[leaf.rx, leaf.ry, leaf.rz]}
          castShadow
        >
          <planeGeometry args={[leaf.w, leaf.h]} />
          <meshStandardMaterial
            color={leafColor}
            roughness={0.75}
            side={THREE.DoubleSide}
            transparent
            opacity={0.93}
          />
        </mesh>
      ))}
    </group>
  );
}

/* ── Brass Hanging Vessel (Shirodhara pot) ─────────────────── */
function BrassVessel({ position }) {
  const vesselRef = useRef();
  useFrame(({ clock }) => {
    if (vesselRef.current) {
      vesselRef.current.rotation.z = Math.sin(clock.getElapsedTime() * 0.35) * 0.025;
      vesselRef.current.position.y =
        position[1] + Math.sin(clock.getElapsedTime() * 0.45) * 0.04;
    }
  });

  // Chain links
  const chainLinks = useMemo(
    () =>
      Array.from({ length: 12 }, (_, i) => ({
        y: i * 0.14,
        rx: i % 2 === 0 ? Math.PI / 2 : 0,
      })),
    []
  );

  const brassMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: new THREE.Color('#b8820a'),
        roughness: 0.22,
        metalness: 0.88,
      }),
    []
  );

  return (
    <group ref={vesselRef} position={position}>
      {/* 3 chains */}
      {[-0.12, 0, 0.12].map((xOff, ci) => (
        <group key={ci} position={[xOff, 0, 0]}>
          {chainLinks.map((link, li) => (
            <mesh key={li} position={[0, link.y + 0.7, 0]} rotation={[link.rx, 0, 0]}>
              <torusGeometry args={[0.03, 0.008, 8, 12]} />
              <primitive object={brassMat} />
            </mesh>
          ))}
        </group>
      ))}
      {/* Vessel body — rounded bottom cylinder */}
      <mesh position={[0, 0, 0]} castShadow material={brassMat}>
        <sphereGeometry args={[0.35, 24, 24, 0, Math.PI * 2, 0, Math.PI * 0.6]} />
      </mesh>
      {/* Rim ring */}
      <mesh position={[0, 0.06, 0]} material={brassMat}>
        <torusGeometry args={[0.35, 0.04, 10, 32]} />
      </mesh>
      {/* Decorative band */}
      <mesh position={[0, -0.1, 0]} material={brassMat}>
        <torusGeometry args={[0.32, 0.025, 8, 32]} />
      </mesh>
      {/* Spout tip */}
      <mesh position={[0, -0.32, 0]} rotation={[Math.PI, 0, 0]} material={brassMat}>
        <coneGeometry args={[0.04, 0.12, 12]} />
      </mesh>
    </group>
  );
}

/* ── Manuscript / Grantha ──────────────────────────────────── */
function Manuscript({ position, rotation = [0, 0, 0], title = 'चरक संहिता' }) {
  const manuscriptRef = useRef();
  useFrame(({ clock }) => {
    if (manuscriptRef.current) {
      manuscriptRef.current.position.y =
        position[1] + Math.sin(clock.getElapsedTime() * 0.3) * 0.015;
    }
  });

  return (
    <group ref={manuscriptRef} position={position} rotation={rotation}>
      {/* Cover */}
      <mesh castShadow>
        <boxGeometry args={[0.65, 0.06, 0.9]} />
        <meshStandardMaterial color="#5c3418" roughness={0.92} />
      </mesh>
      {/* Pages */}
      <mesh position={[0, 0.055, 0]}>
        <boxGeometry args={[0.62, 0.06, 0.87]} />
        <meshStandardMaterial color="#e8dfc0" roughness={0.98} />
      </mesh>
      {/* Spine */}
      <mesh position={[-0.315, 0, 0]}>
        <boxGeometry args={[0.03, 0.15, 0.9]} />
        <meshStandardMaterial color="#4a2810" roughness={0.9} />
      </mesh>
      {/* Page lines suggestion */}
      {[0.2, 0.05, -0.1, -0.25].map((zOff, i) => (
        <mesh key={i} position={[0.05, 0.085, zOff]}>
          <boxGeometry args={[0.48, 0.002, 0.006]} />
          <meshStandardMaterial color="#9a8870" roughness={1} />
        </mesh>
      ))}
    </group>
  );
}

/* ── Medicinal Leaf ─────────────────────────────────────────── */
function MedicinalLeaf({ position, rotation = [0, 0, 0], scale = 1 }) {
  return (
    <mesh position={position} rotation={rotation} scale={scale}>
      <planeGeometry args={[0.2, 0.32]} />
      <meshStandardMaterial
        color="#3d7535"
        roughness={0.75}
        side={THREE.DoubleSide}
        transparent
        opacity={0.9}
      />
    </mesh>
  );
}

/* ── Scene Lighting ─────────────────────────────────────────── */
function SceneLighting() {
  return (
    <>
      {/* Warm ambient fill */}
      <ambientLight intensity={0.35} color="#f5d98a" />

      {/* Main warm sunlight from upper-left */}
      <directionalLight
        position={[-4, 8, 3]}
        intensity={1.8}
        color="#f8d87a"
        castShadow
        shadow-mapSize={[1024, 1024]}
        shadow-camera-near={0.5}
        shadow-camera-far={20}
        shadow-camera-left={-5}
        shadow-camera-right={5}
        shadow-camera-top={5}
        shadow-camera-bottom={-5}
      />

      {/* Warm fill from right */}
      <pointLight position={[4, 3, 2]} intensity={0.8} color="#e8a840" distance={10} />

      {/* Subtle cool rim light from back */}
      <pointLight position={[0, 5, -4]} intensity={0.3} color="#c8d4b0" />

      {/* Incense area glow */}
      <pointLight position={[1.2, -0.8, 0.5]} intensity={0.4} color="#ff8840" distance={3} />
    </>
  );
}

/* ── Wall Background ─────────────────────────────────────────── */
function WallBackground() {
  return (
    <>
      {/* Back wall */}
      <Plane
        args={[14, 8]}
        position={[0, 1.5, -3.5]}
        receiveShadow
      >
        <meshStandardMaterial color="#c8b898" roughness={0.98} />
      </Plane>
      {/* Floor */}
      <Plane
        args={[14, 8]}
        position={[0, -2.35, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        receiveShadow
      >
        <meshStandardMaterial color="#2a1608" roughness={0.95} />
      </Plane>
    </>
  );
}

/* ── Mouse Parallax Camera ───────────────────────────────────── */
function CameraRig({ mouse }) {
  useFrame(({ camera }) => {
    const targetX = (mouse.current[0] * 0.18);
    const targetY = (mouse.current[1] * 0.08);
    camera.position.x += (targetX - camera.position.x) * 0.04;
    camera.position.y += (targetY - camera.position.y) * 0.04;
    camera.lookAt(0, -0.5, 0);
  });
  return null;
}

/* ── Full 3D Scene ───────────────────────────────────────────── */
function SceneContents({ mouse }) {
  return (
    <>
      <CameraRig mouse={mouse} />
      <SceneLighting />
      <WallBackground />

      {/* Table */}
      <Table />

      {/* ── LEFT CLUSTER: Mortar + Poultice balls on tray ── */}
      <WoodenTray position={[-1.9, -1.17, 0.3]} size={[1.4, 0.06, 0.85]} />
      <Mortar position={[-2.2, -1.04, 0.25]} />
      <PoulticeBall position={[-1.6, -0.9, 0.45]} scale={0.9} />
      <PoulticeBall position={[-1.2, -0.92, 0.15]} scale={1.05} />

      {/* Fresh leaves around poultice */}
      <MedicinalLeaf position={[-1.7, -1.18, 0.7]} rotation={[-0.2, 0.8, 0.3]} />
      <MedicinalLeaf position={[-1.5, -1.19, 0.75]} rotation={[-0.15, -0.3, 0.4]} />
      <MedicinalLeaf position={[-1.85, -1.2, 0.6]} rotation={[-0.1, 1.1, 0.2]} />

      {/* ── CENTER: Amber bottles ── */}
      <AmberBottle position={[-0.18, -0.62, 0.3]} variant="tall" />
      <AmberBottle position={[0.38, -0.72, 0.25]} variant="medium" />
      <AmberBottle position={[0.06, -0.99, 0.65]} variant="small" scale={0.9} />

      {/* ── CENTER-RIGHT: Herb bowl with incense ── */}
      <HerbBowl position={[1.1, -1.0, 0.4]} />

      {/* ── Spice bowls ── */}
      <SpiceBowl position={[-0.55, -1.16, -0.2]} powderColor="#d4a020" size={0.14} />
      <SpiceBowl position={[0.5, -1.17, -0.15]} powderColor="#c87040" size={0.12} />
      <SpiceBowl position={[1.7, -1.18, -0.1]} powderColor="#8b5e28" size={0.15} />

      {/* ── Cinnamon sticks ── */}
      <CinnamonStick position={[-0.3, -1.21, -0.4]} rotation={[0, 0.6, Math.PI / 2]} />
      <CinnamonStick position={[-0.15, -1.21, -0.48]} rotation={[0, 0.3, Math.PI / 2 + 0.15]} />
      <CinnamonStick position={[-0.38, -1.21, -0.52]} rotation={[0, 0.9, Math.PI / 2 - 0.1]} />

      {/* ── Manuscripts ── */}
      <Manuscript position={[-2.8, -1.17, -0.6]} rotation={[0, 0.25, 0]} title="चरक संहिता" />
      <Manuscript position={[2.0, -1.19, -0.8]} rotation={[0, -0.15, 0]} title="सुश्रुत संहिता" />

      {/* ── Background potted plants ── */}
      <PottedPlant position={[-2.5, -1.22, -2.0]} scale={1.5} plantType="ficus" />
      <PottedPlant position={[0.2, -1.22, -2.5]} scale={1.2} plantType="fern" />
      <PottedPlant position={[2.8, -1.22, -2.2]} scale={1.1} plantType="ficus" />

      {/* ── Brass hanging vessel (upper right) ── */}
      <BrassVessel position={[2.6, 1.8, -0.5]} />
    </>
  );
}

/* ── Main export ─────────────────────────────────────────────── */
export default function AyurvedicScene({ mouse }) {
  return (
    <Canvas
      camera={{ position: [0, 0.5, 5.5], fov: 48 }}
      shadows
      gl={{ antialias: true, alpha: true }}
      style={{ width: '100%', height: '100%' }}
      aria-label="3D Ayurvedic apothecary environment"
      role="img"
    >
      <Suspense fallback={null}>
        <SceneContents mouse={mouse} />
      </Suspense>
    </Canvas>
  );
}
