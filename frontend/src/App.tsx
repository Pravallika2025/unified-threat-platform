import { AppRoutes } from "@/app/router";
import { Providers } from "@/app/providers";

export default function App() {
  return (
    <Providers>
      <AppRoutes />
    </Providers>
  );
}
