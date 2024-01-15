import type { SVGProps } from 'react';

import { useEffect, useRef } from 'react';
import createGlobe from 'cobe';
import { useSpring } from 'react-spring';
import { YoutubeIcon } from 'lucide-react';

import { SlackWhiteIcon, DiscordIcon, LarkWhiteIcon, TelegramIcon } from '@/components/icons';

export const Logo = (props: SVGProps<SVGSVGElement>) => (
  <svg fill="none" viewBox="0 0 423 120" xmlns="http://www.w3.org/2000/svg" {...props}>
    <path
      d="M37.7068 91.6339C10.1634 91.6339 0.709893 74.3609 0.709893 46.2339C0.709893 17.29 13.0811 0.833968 40.7412 0.833968C55.0965 0.833968 63.0327 6.90286 66.4173 10.2874L58.2477 24.0592C55.9135 21.8417 50.6615 18.3404 42.1418 18.3404C25.8024 18.3404 19.6168 27.5604 19.6168 46.2339C19.6168 65.7244 25.4523 74.1275 39.1073 74.1275C42.842 74.1275 46.1099 73.544 47.1603 72.727V56.0375H35.606V39.3481H65.8338V84.6314C60.115 88.7162 50.3114 91.6339 37.7068 91.6339ZM96.2512 90H77.6944V31.6453H96.2512V90ZM76.5273 14.7224C76.5273 8.77021 81.0789 4.21855 87.0311 4.21855C92.9833 4.21855 97.535 8.77021 97.535 14.7224C97.535 20.6746 92.9833 25.2263 87.0311 25.2263C81.0789 25.2263 76.5273 20.6746 76.5273 14.7224ZM142.091 74.4776L147.693 87.199C145.008 89.4165 140.223 91.6339 131.703 91.6339C119.449 91.6339 113.38 84.9815 113.38 72.0267V47.1676H103.927V33.3959L113.38 31.9954V19.0406L132.054 16.3563V31.6453H146.526V47.1676H132.054V70.3928C132.054 75.0612 133.921 76.4617 136.839 76.4617C139.64 76.4617 141.04 75.4113 142.091 74.4776ZM223.863 37.0139L209.158 90H187.916L173.211 37.0139L173.795 90H155.354V2.4679H181.731L198.537 65.2576L215.343 2.4679H241.719V90H223.279L223.863 37.0139ZM283.622 52.8864V50.2021C283.622 47.0509 281.404 45.0669 274.985 45.0669C269.383 45.0669 263.081 47.1676 258.529 51.2525L251.177 38.7645C255.261 35.2633 262.731 30.0113 277.203 30.0113C295.76 30.0113 301.712 39.1147 301.712 51.4859V90H290.508L287.94 85.565C283.739 89.2997 277.786 91.6339 270.784 91.6339C255.845 91.6339 250.943 81.8303 250.943 73.0771C250.943 57.3214 262.497 54.8704 273.001 53.9368L283.622 52.8864ZM283.622 63.0401L275.802 64.0905C270.55 64.9075 268.45 67.3584 268.45 71.91C268.45 76.2283 271.134 78.7959 275.219 78.7959C278.603 78.7959 281.754 77.8622 283.622 75.9949V63.0401ZM308.136 31.6453H328.327L337.897 65.9579L347.467 31.6453H367.658L334.279 119.177H313.855L329.027 86.1486L308.136 31.6453ZM404.717 52.8864V50.2021C404.717 47.0509 402.5 45.0669 396.081 45.0669C390.478 45.0669 384.176 47.1676 379.624 51.2525L372.272 38.7645C376.357 35.2633 383.826 30.0113 398.298 30.0113C416.855 30.0113 422.807 39.1147 422.807 51.4859V90H411.603L409.035 85.565C404.834 89.2997 398.882 91.6339 391.879 91.6339C376.94 91.6339 372.038 81.8303 372.038 73.0771C372.038 57.3214 383.593 54.8704 394.096 53.9368L404.717 52.8864ZM404.717 63.0401L396.897 64.0905C391.646 64.9075 389.545 67.3584 389.545 71.91C389.545 76.2283 392.229 78.7959 396.314 78.7959C399.698 78.7959 402.85 77.8622 404.717 75.9949V63.0401Z"
      fill="CurrentColor"
    />
  </svg>
);

export function Cobe() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const canvasRef = useRef<any>();
  const pointerInteracting = useRef<number | null>(0);
  const pointerInteractionMovement = useRef(0);
  const [{ r }, api] = useSpring(() => ({
    r: 0,
    config: {
      mass: 1,
      tension: 280,
      friction: 40,
      precision: 0.001,
    },
  }));

  useEffect(() => {
    let phi = 0;
    let width = 0;
    const onResize = () => canvasRef.current && (width = canvasRef.current.offsetWidth);

    window.addEventListener('resize', onResize);
    onResize();
    const globe = createGlobe(canvasRef.current, {
      devicePixelRatio: 2,
      width: width * 2,
      height: width * 2,
      phi: 0,
      theta: 0.2,
      dark: 1.2,
      diffuse: 3,
      mapSamples: 22000,
      mapBrightness: 1.6,
      mapBaseBrightness: 0.09,
      baseColor: [1.1, 1.1, 1.1],
      markerColor: [251 / 255, 100 / 255, 21 / 255],
      glowColor: [1.1, 1.1, 1.1],
      markers: [],
      opacity: 0.8,
      onRender: (state) => {
        // `state` will be an empty object, return updated params.
        state.phi = phi + r.get();
        phi += 0.006;
        state.width = width * 2;
        state.height = width * 2;
      },
    });

    setTimeout(() => (canvasRef.current.style.opacity = '1'));

    return () => globe.destroy();
  }, []);

  return (
    <div
      style={{
        width: '100%',
        maxWidth: 700,
        aspectRatio: 1,
        margin: 'auto',
        position: 'relative',
      }}
    >
      <div
        className={'group  cursor-pointer'}
        style={{
          width: '100%',
          fontWeight: 700,
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 1,
          textAlign: 'center',
          color: '#fff',
          userSelect: 'none',
          position: 'absolute',
          mixBlendMode: 'difference',
        }}
      >
        <Logo
          className={'w-40 group-hover:opacity-85 md:w-[400px]'}
          style={{
            margin: 'auto',
            display: 'block',
            marginBottom: 2,
          }}
        />
        <div className={'flex items-center justify-center'}>
          <div className={'flex  items-center justify-center px-12'}>
            <YoutubeIcon className={'size-6 pt-0.5 group-hover:text-maya md:size-10'} />
            <span
              className={'text-xl group-hover:opacity-85 md:text-4xl '}
              style={{ paddingLeft: '10px' }}
            >
              Make Git Flow In Chat
            </span>
          </div>
        </div>
        <div
          className={
            'mt-4 flex items-center justify-center gap-5 text-2xl group-hover:opacity-85 md:mt-6 md:text-4xl'
          }
        >
          <LarkWhiteIcon />
          <DiscordIcon />
          <SlackWhiteIcon />
          <TelegramIcon />
        </div>
      </div>
      <canvas
        ref={canvasRef}
        style={{
          width: '100%',
          height: '100%',
          cursor: 'grab',
          zIndex: 0,
          contain: 'layout paint size',
          opacity: 0,
          transition: 'opacity 1s ease',
          borderRadius: '50%',
        }}
        onMouseMove={(e) => {
          if (pointerInteracting.current !== null) {
            const delta = e.clientX - pointerInteracting.current;

            pointerInteractionMovement.current = delta;
            api.start({
              r: delta / 200,
            });
          }
        }}
        onPointerDown={(e) => {
          pointerInteracting.current = e.clientX - pointerInteractionMovement.current;
          canvasRef.current.style.cursor = 'grabbing';
        }}
        onPointerOut={() => {
          pointerInteracting.current = null;
          canvasRef.current.style.cursor = 'grab';
        }}
        onPointerUp={() => {
          pointerInteracting.current = null;
          canvasRef.current.style.cursor = 'grab';
        }}
        onTouchMove={(e) => {
          if (pointerInteracting.current !== null && e.touches[0]) {
            const delta = e.touches[0].clientX - pointerInteracting.current;

            pointerInteractionMovement.current = delta;
            api.start({
              r: delta / 100,
            });
          }
        }}
      />
    </div>
  );
}
