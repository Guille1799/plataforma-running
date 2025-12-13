'use client';

import React from 'react';
import { Button } from '@/app/components/ui/button';
import { Card, CardContent } from '@/app/components/ui/card';
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react';
import { format, subDays, subWeeks, subMonths, startOfMonth, endOfMonth } from 'date-fns';
import { es } from 'date-fns/locale';

interface DateRange {
    from: Date;
    to: Date;
}

interface DateRangeFilterProps {
    dateRange: DateRange;
    onDateRangeChange: (range: DateRange) => void;
}

export function DateRangeFilter({ dateRange, onDateRangeChange }: DateRangeFilterProps) {
    const presets = [
        {
            label: 'Última Semana',
            getValue: () => ({
                from: subDays(new Date(), 7),
                to: new Date(),
            }),
        },
        {
            label: 'Últimas 2 Semanas',
            getValue: () => ({
                from: subWeeks(new Date(), 2),
                to: new Date(),
            }),
        },
        {
            label: 'Último Mes',
            getValue: () => ({
                from: subMonths(new Date(), 1),
                to: new Date(),
            }),
        },
        {
            label: 'Este Mes',
            getValue: () => {
                const now = new Date();
                return {
                    from: startOfMonth(now),
                    to: endOfMonth(now),
                };
            },
        },
        {
            label: 'Últimos 3 Meses',
            getValue: () => ({
                from: subMonths(new Date(), 3),
                to: new Date(),
            }),
        },
    ];

    const moveBackward = () => {
        const rangeLength = dateRange.to.getTime() - dateRange.from.getTime();
        const newFrom = new Date(dateRange.from.getTime() - rangeLength);
        const newTo = new Date(dateRange.from.getTime());
        onDateRangeChange({ from: newFrom, to: newTo });
    };

    const moveForward = () => {
        const rangeLength = dateRange.to.getTime() - dateRange.from.getTime();
        const newFrom = new Date(dateRange.to.getTime());
        const newTo = new Date(dateRange.to.getTime() + rangeLength);
        
        // No permitir ir al futuro
        const now = new Date();
        if (newFrom > now) return;
        
        onDateRangeChange({
            from: newFrom,
            to: newTo > now ? now : newTo,
        });
    };

    const isCurrentRange = () => {
        const now = new Date();
        const diffDays = Math.floor((now.getTime() - dateRange.to.getTime()) / (1000 * 60 * 60 * 24));
        return Math.abs(diffDays) <= 1;
    };

    return (
        <Card className="bg-slate-900 border-slate-800">
            <CardContent className="pt-6">
                <div className="space-y-4">
                    {/* Current Range Display */}
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Calendar className="h-5 w-5 text-blue-500" />
                            <div>
                                <p className="text-sm text-slate-400">Período Análisis</p>
                                <p className="text-lg font-semibold text-white">
                                    {format(dateRange.from, 'd MMM', { locale: es })} -{' '}
                                    {format(dateRange.to, 'd MMM yyyy', { locale: es })}
                                </p>
                            </div>
                        </div>
                        {isCurrentRange() && (
                            <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                                Hoy
                            </span>
                        )}
                    </div>

                    {/* Navigation Buttons */}
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={moveBackward}
                            className="bg-slate-800 border-slate-700 hover:bg-slate-700"
                        >
                            <ChevronLeft className="h-4 w-4 mr-1" />
                            Anterior
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onDateRangeChange({ from: subDays(new Date(), 7), to: new Date() })}
                            className="bg-slate-800 border-slate-700 hover:bg-slate-700 flex-1"
                        >
                            Hoy
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={moveForward}
                            disabled={isCurrentRange()}
                            className="bg-slate-800 border-slate-700 hover:bg-slate-700"
                        >
                            Siguiente
                            <ChevronRight className="h-4 w-4 ml-1" />
                        </Button>
                    </div>

                    {/* Preset Buttons */}
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                        {presets.map((preset) => (
                            <Button
                                key={preset.label}
                                variant="ghost"
                                size="sm"
                                onClick={() => onDateRangeChange(preset.getValue())}
                                className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300"
                            >
                                {preset.label}
                            </Button>
                        ))}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

export default DateRangeFilter;
