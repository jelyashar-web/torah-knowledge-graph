"use client";

import { ApolloProvider as BaseProvider } from "@apollo/client/react";
import { apolloClient } from "@/lib/apollo-client";

export function ApolloProvider({ children }: { children: React.ReactNode }) {
  return <BaseProvider client={apolloClient}>{children}</BaseProvider>;
}
