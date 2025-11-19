'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
      setSuccess('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Por favor selecciona un archivo');
      return;
    }

    setIsUploading(true);
    setError('');
    setSuccess('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://127.0.0.1:8000/api/v1/upload/workout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiClient.getToken()}`
        },
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al subir archivo');
      }

      const data = await response.json();
      setSuccess(`✅ Entrenamiento subido: ${data.workout.distance_km}km en ${data.workout.duration_minutes} min`);
      setFile(null);
      
      // Reset file input
      const fileInput = document.getElementById('file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';

      // Redirect after 2 seconds
      setTimeout(() => {
        router.push('/dashboard/workouts');
      }, 2000);

    } catch (err: any) {
      setError(err.message || 'Error al subir el archivo');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError('');
      setSuccess('');
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  return (
    <div className="p-8">
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">Subir Entrenamiento</h1>
          <p className="text-slate-400">
            Sube archivos FIT, GPX o TCX desde cualquier dispositivo
          </p>
        </div>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">📁 Archivo de Entrenamiento</CardTitle>
            <CardDescription className="text-slate-400">
              Formatos soportados: .fit (Garmin/Wahoo/Polar), .gpx (Universal), .tcx (Garmin)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Drag & Drop Zone */}
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              className="border-2 border-dashed border-slate-600 rounded-lg p-12 text-center hover:border-blue-500 transition-colors cursor-pointer"
              onClick={() => document.getElementById('file-input')?.click()}
            >
              {file ? (
                <div>
                  <p className="text-white text-lg mb-2">📄 {file.name}</p>
                  <p className="text-slate-400 text-sm">
                    {(file.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              ) : (
                <div>
                  <p className="text-white text-lg mb-2">
                    Arrastra un archivo aquí o haz click para seleccionar
                  </p>
                  <p className="text-slate-400 text-sm">
                    FIT, GPX, TCX
                  </p>
                </div>
              )}
            </div>

            {/* Hidden File Input */}
            <input
              id="file-input"
              type="file"
              accept=".fit,.gpx,.tcx"
              onChange={handleFileChange}
              className="hidden"
            />

            {/* Upload Button */}
            <Button
              onClick={handleUpload}
              disabled={!file || isUploading}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              {isUploading ? 'Subiendo...' : 'Subir Entrenamiento'}
            </Button>

            {/* Error Message */}
            {error && (
              <div className="bg-red-500/10 border border-red-500 rounded-lg p-4">
                <p className="text-red-400">{error}</p>
              </div>
            )}

            {/* Success Message */}
            {success && (
              <div className="bg-green-500/10 border border-green-500 rounded-lg p-4">
                <p className="text-green-400">{success}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Supported Devices */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">📱 Dispositivos Compatibles</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="text-center p-4">
                <p className="text-slate-200 font-semibold">Garmin</p>
                <p className="text-slate-400 text-sm">.fit</p>
              </div>
              <div className="text-center p-4">
                <p className="text-slate-200 font-semibold">Wahoo</p>
                <p className="text-slate-400 text-sm">.fit</p>
              </div>
              <div className="text-center p-4">
                <p className="text-slate-200 font-semibold">Polar</p>
                <p className="text-slate-400 text-sm">.fit, .gpx</p>
              </div>
              <div className="text-center p-4">
                <p className="text-slate-200 font-semibold">Suunto</p>
                <p className="text-slate-400 text-sm">.fit, .gpx</p>
              </div>
              <div className="text-center p-4">
                <p className="text-slate-200 font-semibold">Coros</p>
                <p className="text-slate-400 text-sm">.fit</p>
              </div>
              <div className="text-center p-4">
                <p className="text-slate-200 font-semibold">Xiaomi/Amazfit</p>
                <p className="text-slate-400 text-sm">.gpx, .tcx</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="text-center">
          <Button
            onClick={() => router.back()}
            variant="outline"
            className="border-slate-600 text-slate-300 hover:bg-slate-700"
          >
            Volver
          </Button>
        </div>
      </div>
    </div>
  );
}
