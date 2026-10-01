import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { App } from "./app";

describe("app bootstrap", () => {
  it("renders the application shell", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "Cueva de las Pavas" })).toBeInTheDocument();
  });
});
