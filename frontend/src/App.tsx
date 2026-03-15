import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import ProjectList from "./pages/ProjectList";
import ProjectDetail from "./pages/ProjectDetail";
import QueryView from "./pages/QueryView";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<ProjectList />} />
        <Route path="/projects/:id" element={<ProjectDetail />} />
      </Route>
      <Route path="/projects/:projectId/query" element={<QueryView />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
