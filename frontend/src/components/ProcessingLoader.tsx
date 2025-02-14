import { motion, useAnimation } from "framer-motion";
import { useEffect } from "react";

export default function ProcessingLoader() {
    const controls = useAnimation();

    useEffect(() => {
        const animate = async () => {
            while (true) {
                // Flip forward
                await controls.start({
                    rotateY: 360,
                    transition: {
                        duration: 2,
                        ease: "easeInOut",
                    }
                });
                // Slow down
                await controls.start({
                    rotateY: 720,
                    transition: {
                        duration: 3,
                        ease: "easeInOut",
                    }
                });
                // Flip backward
                await controls.start({
                    rotateY: 360,
                    transition: {
                        duration: 2,
                        ease: "easeInOut",
                    }
                });
                // Slow down again
                await controls.start({
                    rotateY: 0,
                    transition: {
                        duration: 3,
                        ease: "easeInOut",
                    }
                });
            }
        };

        animate();
    }, [controls]);

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col items-center"
        >
            <div className="perspective-[1000px]">
                <motion.div
                    animate={controls}
                    className="w-20 h-28 bg-white border-2 border-black rounded-lg shadow-lg"
                    style={{
                        transformStyle: "preserve-3d"
                    }}
                />
            </div>
            <p className="mt-8 text-lg text-[#767676]">
                Processing your files...grab a coffee! ☕️
            </p>
        </motion.div>
    );
}