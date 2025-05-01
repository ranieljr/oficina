import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from "@/components/ui/button";

const NotFoundPage = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-150px)] text-center">
      <h1 className="text-6xl font-bold text-gray-800 mb-4">404</h1>
      <p className="text-xl text-gray-600 mb-8">Oops! A página que você está procurando não foi encontrada.</p>
      <Link to="/">
        <Button>Voltar para a Página Inicial</Button>
      </Link>
    </div>
  );
};

export default NotFoundPage;

