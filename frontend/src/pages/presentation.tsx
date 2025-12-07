import React, { useState, useEffect } from 'react'
import Head from 'next/head'

export default function PresentationPage() {
  const [currentSlide, setCurrentSlide] = useState(0)
  const [direction, setDirection] = useState<'next' | 'prev'>('next')

  const slides = [
    {
      id: 'intro',
      title: 'QuantIA',
      subtitle: 'El Núcleo de la Vida Digital',
      content: (
        <div className="space-y-8">
          <p className="text-2xl text-gray-300 leading-relaxed">
            Una nueva era de salud viva: un ecosistema médico inteligente diseñado para acompañar a cada persona durante toda su vida,
            comprendiendo su cuerpo, mente y entorno.
          </p>
          <div className="border-l-4 border-blue-500 pl-6 py-4 bg-gray-800/50 rounded-r">
            <p className="text-xl text-gray-200 italic">
              "Del nacimiento a la madurez, QuantIA recuerda, entiende y predice para proteger tu salud."
            </p>
          </div>
          <div className="text-sm text-gray-500 mt-12">
            Desarrollado por <span className="text-blue-400 font-semibold">quantumq Lab</span>
          </div>
        </div>
      )
    },
    {
      id: 'concept',
      title: 'Concepto Mental',
      subtitle: 'La mente digital que concentra y organiza la historia completa de una persona',
      content: (
        <div className="space-y-6">
          <p className="text-xl text-gray-300 leading-relaxed">
            QuantIA integra datos médicos, biológicos, emocionales y de estilo de vida para construir una representación holística del individuo.
          </p>
          <div className="grid grid-cols-3 gap-4 my-8">
            <div className="bg-gradient-to-br from-blue-900/40 to-blue-800/20 p-6 rounded-lg border border-blue-700/30">
              <div className="text-center text-blue-400 font-semibold mb-2">Persona Humana</div>
            </div>
            <div className="bg-gradient-to-br from-purple-900/40 to-purple-800/20 p-6 rounded-lg border border-purple-700/30 flex items-center justify-center">
              <div className="text-center text-purple-300 font-bold text-lg">Núcleo QuantIA</div>
            </div>
            <div className="bg-gradient-to-br from-green-900/40 to-green-800/20 p-6 rounded-lg border border-green-700/30">
              <div className="text-center text-green-400 font-semibold mb-2">Agentes Inteligentes</div>
            </div>
          </div>
          <div className="bg-gray-800/50 p-6 rounded-lg border border-gray-700">
            <p className="text-gray-300">
              QuantIA no almacena solo registros, sino <span className="text-blue-400 font-semibold">contexto</span>: 
              entiende causas, patrones y relaciones a lo largo del tiempo.
            </p>
          </div>
        </div>
      )
    },
    {
      id: 'consciousness',
      title: 'Tres Niveles de Conciencia Médica',
      subtitle: 'Arquitectura cognitiva para comprensión integral de la salud',
      content: (
        <div className="space-y-6">
          <div className="grid gap-6">
            <div className="bg-gradient-to-r from-blue-900/30 to-transparent p-6 rounded-lg border-l-4 border-blue-500">
              <h3 className="text-2xl font-bold text-blue-400 mb-3">Episódico</h3>
              <p className="text-gray-300 mb-2">Registra los eventos de salud: consultas, diagnósticos, análisis, emociones.</p>
              <p className="text-sm text-gray-500 italic">"Qué pasó y cuándo."</p>
            </div>
            <div className="bg-gradient-to-r from-purple-900/30 to-transparent p-6 rounded-lg border-l-4 border-purple-500">
              <h3 className="text-2xl font-bold text-purple-400 mb-3">Semántico</h3>
              <p className="text-gray-300 mb-2">Aprende conceptos sobre tu cuerpo, hábitos y riesgos.</p>
              <p className="text-sm text-gray-500 italic">"Qué significa lo que pasa."</p>
            </div>
            <div className="bg-gradient-to-r from-green-900/30 to-transparent p-6 rounded-lg border-l-4 border-green-500">
              <h3 className="text-2xl font-bold text-green-400 mb-3">Predictivo</h3>
              <p className="text-gray-300 mb-2">Proyecta tu evolución futura según patrones personales.</p>
              <p className="text-sm text-gray-500 italic">"Qué podría pasar y cómo prevenirlo."</p>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'architecture',
      title: 'Arquitectura Conceptual',
      subtitle: 'Cinco módulos mentales, cada uno con una función cognitiva distinta',
      content: (
        <div className="space-y-4">
          <div className="grid gap-4">
            <div className="flex items-start gap-4 bg-gray-800/30 p-4 rounded-lg border border-gray-700/50 hover:border-blue-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/20">
              <div className="flex-1">
                <h4 className="font-bold text-blue-400 mb-1">Motor BioContexto</h4>
                <p className="text-sm text-gray-400">Comprende tu biología y genética. Analítica médica y biomolecular.</p>
              </div>
            </div>
            <div className="flex items-start gap-4 bg-gray-800/30 p-4 rounded-lg border border-gray-700/50 hover:border-purple-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/20">
              <div className="flex-1">
                <h4 className="font-bold text-purple-400 mb-1">Conciencia Temporal</h4>
                <p className="text-sm text-gray-400">Organiza tu vida médica en una línea temporal inteligente. Memoria episódica.</p>
              </div>
            </div>
            <div className="flex items-start gap-4 bg-gray-800/30 p-4 rounded-lg border border-gray-700/50 hover:border-green-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-green-500/20">
              <div className="flex-1">
                <h4 className="font-bold text-green-400 mb-1">PsicoSentido</h4>
                <p className="text-sm text-gray-400">Percibe emociones, tono de voz, sueño, estrés y bienestar. IA emocional y contextual.</p>
              </div>
            </div>
            <div className="flex items-start gap-4 bg-gray-800/30 p-4 rounded-lg border border-gray-700/50 hover:border-yellow-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-yellow-500/20">
              <div className="flex-1">
                <h4 className="font-bold text-yellow-400 mb-1">Núcleo de Integración</h4>
                <p className="text-sm text-gray-400">Funde datos médicos, ambientales y de estilo de vida. Razonamiento simbólico.</p>
              </div>
            </div>
            <div className="flex items-start gap-4 bg-gray-800/30 p-4 rounded-lg border border-gray-700/50 hover:border-red-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-red-500/20">
              <div className="flex-1">
                <h4 className="font-bold text-red-400 mb-1">Guardián Ético</h4>
                <p className="text-sm text-gray-400">Protege tu privacidad y decisiones. Gobernanza ética y consentimiento activo.</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'thinking',
      title: 'Cómo Piensa QuantIA',
      subtitle: 'Red de razonamiento en tiempo real',
      content: (
        <div className="space-y-6">
          <div className="grid gap-4">
            {[
              { num: '01', title: 'Percibe', desc: 'Recibe señales: sensores, voz, resultados médicos', color: 'blue' },
              { num: '02', title: 'Comprende', desc: 'Interpreta su significado según tu contexto histórico', color: 'purple' },
              { num: '03', title: 'Predice', desc: 'Genera hipótesis o alertas anticipadas', color: 'green' },
              { num: '04', title: 'Actúa', desc: 'Sugiere acciones, notifica al médico o ajusta rutinas', color: 'yellow' },
              { num: '05', title: 'Aprende', desc: 'Integra cada nueva experiencia para futuras decisiones', color: 'red' }
            ].map((step) => (
              <div key={step.num} className={`flex items-center gap-4 bg-gradient-to-r from-${step.color}-900/20 to-transparent p-4 rounded-lg border-l-4 border-${step.color}-500`}>
                <div className={`text-3xl font-bold text-${step.color}-400 w-16`}>{step.num}</div>
                <div className="flex-1">
                  <h4 className={`font-bold text-${step.color}-400 mb-1`}>{step.title}</h4>
                  <p className="text-sm text-gray-400">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )
    },
    {
      id: 'privacy',
      title: 'Filosofía de Privacidad',
      subtitle: 'Intimidad segura: tus datos, tu control',
      content: (
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-red-900/20 to-purple-900/20 p-8 rounded-lg border border-red-700/30">
            <p className="text-xl text-gray-200 leading-relaxed mb-6">
              Tus datos son <span className="text-red-400 font-bold">tuyos</span>, y el sistema es solo 
              su <span className="text-purple-400 font-bold">guardián inteligente</span>.
            </p>
            <ul className="space-y-4 text-gray-300">
              <li className="flex items-start gap-3">
                <span className="text-green-400 mt-1 font-bold">•</span>
                <span>Todo se cifra en múltiples capas</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-green-400 mt-1 font-bold">•</span>
                <span>Cada acción requiere tu consentimiento dinámico (ConsentimientoInteligente)</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-green-400 mt-1 font-bold">•</span>
                <span>QuantIA olvida activamente lo que tú eliges borrar</span>
              </li>
            </ul>
          </div>
          <div className="border-l-4 border-purple-500 pl-6 py-4 bg-gray-800/50 rounded-r">
            <p className="text-lg text-gray-300 italic">
              "No solo recuerda bien, sino que olvida con respeto."
            </p>
          </div>
        </div>
      )
    },
    {
      id: 'vital-connection',
      title: 'La Conexión Vital',
      subtitle: 'Tu línea de vida de salud a través del tiempo',
      content: (
        <div className="space-y-6">
          <p className="text-xl text-gray-300 leading-relaxed">
            QuantIA es el puente entre tú, tus médicos y tus versiones pasadas y futuras.
            Permite comprender tu línea vital de salud y actuar antes de que el cuerpo lo pida.
          </p>
          <div className="bg-gray-800/30 p-6 rounded-lg border border-gray-700">
            <h4 className="text-lg font-bold text-blue-400 mb-4">Ejemplo de Línea Vital de Salud:</h4>
            <div className="space-y-3">
              <div className="flex items-center gap-4">
                <div className="w-20 text-blue-400 font-bold">0 años</div>
                <div className="flex-1 h-2 bg-gradient-to-r from-blue-500 to-blue-700 rounded"></div>
                <div className="text-gray-400">ADN y nacimiento</div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-20 text-purple-400 font-bold">10 años</div>
                <div className="flex-1 h-2 bg-gradient-to-r from-purple-500 to-purple-700 rounded"></div>
                <div className="text-gray-400">Alergias y vacunas</div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-20 text-green-400 font-bold">25 años</div>
                <div className="flex-1 h-2 bg-gradient-to-r from-green-500 to-green-700 rounded"></div>
                <div className="text-gray-400">Estrés laboral</div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-20 text-yellow-400 font-bold">35 años</div>
                <div className="flex-1 h-2 bg-gradient-to-r from-yellow-500 to-yellow-700 rounded"></div>
                <div className="text-gray-400">Control cardiovascular preventivo</div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-20 text-red-400 font-bold">60 años</div>
                <div className="flex-1 h-2 bg-gradient-to-r from-red-500 to-red-700 rounded"></div>
                <div className="text-gray-400">Monitoreo de envejecimiento activo</div>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'data-sources',
      title: 'Fuentes de Datos Integradas',
      subtitle: 'Recopilación holística y continua de información de salud',
      content: (
        <div className="space-y-6">
          <p className="text-lg text-gray-300 mb-6">
            QuantIA integra datos de múltiples fuentes para construir un perfil completo y en tiempo real de tu salud.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Fila 1 */}
            <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/10 p-5 rounded-lg border border-blue-700/30 hover:border-blue-500/50 transition-all">
              <h4 className="font-bold text-blue-400 mb-2">Análisis Clínicos</h4>
              <p className="text-sm text-gray-400">Resultados de laboratorio, bioquímica, hematología, perfiles lipídicos, HbA1c</p>
            </div>
            
            <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/10 p-5 rounded-lg border border-purple-700/30 hover:border-purple-500/50 transition-all">
              <h4 className="font-bold text-purple-400 mb-2">Consultas Médicas</h4>
              <p className="text-sm text-gray-400">Notas clínicas, diagnósticos, planes de tratamiento, recetas, recomendaciones</p>
            </div>

            {/* Fila 2 */}
            <div className="bg-gradient-to-br from-green-900/30 to-green-800/10 p-5 rounded-lg border border-green-700/30 hover:border-green-500/50 transition-all">
              <h4 className="font-bold text-green-400 mb-2">Dispositivos Wearables</h4>
              <p className="text-sm text-gray-400">Apple Watch, Fitbit, Garmin: ritmo cardíaco, pasos, sueño, VO2 max, ECG</p>
            </div>
            
            <div className="bg-gradient-to-br from-yellow-900/30 to-yellow-800/10 p-5 rounded-lg border border-yellow-700/30 hover:border-yellow-500/50 transition-all">
              <h4 className="font-bold text-yellow-400 mb-2">Hospitales y Clínicas</h4>
              <p className="text-sm text-gray-400">Historias clínicas electrónicas (EHR/EMR), ingresos, procedimientos, cirugías</p>
            </div>

            {/* Fila 3 */}
            <div className="bg-gradient-to-br from-red-900/30 to-red-800/10 p-5 rounded-lg border border-red-700/30 hover:border-red-500/50 transition-all">
              <h4 className="font-bold text-red-400 mb-2">Imágenes Médicas</h4>
              <p className="text-sm text-gray-400">Rayos X, Tomografías (CT), Resonancias (MRI), Ecografías, PET Scans</p>
            </div>
            
            <div className="bg-gradient-to-br from-indigo-900/30 to-indigo-800/10 p-5 rounded-lg border border-indigo-700/30 hover:border-indigo-500/50 transition-all">
              <h4 className="font-bold text-indigo-400 mb-2">Laboratorios Externos</h4>
              <p className="text-sm text-gray-400">Patología, microbiología, genética, pruebas especializadas</p>
            </div>

            {/* Fila 4 */}
            <div className="bg-gradient-to-br from-pink-900/30 to-pink-800/10 p-5 rounded-lg border border-pink-700/30 hover:border-pink-500/50 transition-all">
              <h4 className="font-bold text-pink-400 mb-2">Farmacias y Medicación</h4>
              <p className="text-sm text-gray-400">Historial de prescripciones, adherencia, interacciones medicamentosas</p>
            </div>
            
            <div className="bg-gradient-to-br from-teal-900/30 to-teal-800/10 p-5 rounded-lg border border-teal-700/30 hover:border-teal-500/50 transition-all">
              <h4 className="font-bold text-teal-400 mb-2">Monitoreo Continuo</h4>
              <p className="text-sm text-gray-400">Glucómetros (CGM), tensiómetros, oxímetros, báscula inteligente</p>
            </div>

            {/* Fila 5 */}
            <div className="bg-gradient-to-br from-orange-900/30 to-orange-800/10 p-5 rounded-lg border border-orange-700/30 hover:border-orange-500/50 transition-all">
              <h4 className="font-bold text-orange-400 mb-2">Aplicaciones de Salud</h4>
              <p className="text-sm text-gray-400">Apps de nutrición, ejercicio, meditación, ciclos menstruales, salud mental</p>
            </div>
            
            <div className="bg-gradient-to-br from-cyan-900/30 to-cyan-800/10 p-5 rounded-lg border border-cyan-700/30 hover:border-cyan-500/50 transition-all">
              <h4 className="font-bold text-cyan-400 mb-2">Datos Genéticos</h4>
              <p className="text-sm text-gray-400">Secuenciación de ADN, pruebas de ancestría, predisposiciones genéticas</p>
            </div>

            {/* Fila 6 */}
            <div className="bg-gradient-to-br from-lime-900/30 to-lime-800/10 p-5 rounded-lg border border-lime-700/30 hover:border-lime-500/50 transition-all">
              <h4 className="font-bold text-lime-400 mb-2">Seguros de Salud</h4>
              <p className="text-sm text-gray-400">Historial de coberturas, autorizaciones, reclamaciones, planes activos</p>
            </div>
            
            <div className="bg-gradient-to-br from-amber-900/30 to-amber-800/10 p-5 rounded-lg border border-amber-700/30 hover:border-amber-500/50 transition-all">
              <h4 className="font-bold text-amber-400 mb-2">Registro Manual</h4>
              <p className="text-sm text-gray-400">Síntomas, estado de ánimo, diarios de salud, notas personales</p>
            </div>
          </div>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-400 italic">
              Integración automática mediante APIs, HL7 FHIR, DICOM, y conectores personalizados
            </p>
          </div>
        </div>
      )
    },
    {
      id: 'agents',
      title: 'Ecosistema de Agentes',
      subtitle: 'Red inteligente para cuidado integral',
      content: (
        <div className="space-y-6">
          <p className="text-lg text-gray-300">
            QuantIA se comunica con un ecosistema de agentes inteligentes, cada uno alimentando y consultando al núcleo 
            para asegurar que cada decisión se tome con la comprensión completa de tu historia.
          </p>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/10 p-6 rounded-lg border border-blue-700/30">
              <h4 className="font-bold text-blue-400 mb-2">BioAgente</h4>
              <p className="text-sm text-gray-400">Analiza tus biomarcadores</p>
            </div>
            <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/10 p-6 rounded-lg border border-purple-700/30">
              <h4 className="font-bold text-purple-400 mb-2">MenteAgente</h4>
              <p className="text-sm text-gray-400">Observa tu salud emocional</p>
            </div>
            <div className="bg-gradient-to-br from-green-900/30 to-green-800/10 p-6 rounded-lg border border-green-700/30">
              <h4 className="font-bold text-green-400 mb-2">EstiloVidaAgente</h4>
              <p className="text-sm text-gray-400">Guía tu nutrición y ejercicio</p>
            </div>
            <div className="bg-gradient-to-br from-yellow-900/30 to-yellow-800/10 p-6 rounded-lg border border-yellow-700/30">
              <h4 className="font-bold text-yellow-400 mb-2">EnlaceMédico</h4>
              <p className="text-sm text-gray-400">Interactúa con profesionales humanos</p>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'purpose',
      title: 'Propósito Trascendental',
      subtitle: 'Redefiniendo la relación entre humanos y salud',
      content: (
        <div className="space-y-8">
          <p className="text-2xl text-gray-200 leading-relaxed">
            QuantIA transforma el cuidado médico en un proceso <span className="text-blue-400 font-bold">continuo, empático y personalizado</span>.
          </p>
          <div className="bg-gradient-to-br from-blue-900/30 via-purple-900/30 to-green-900/30 p-8 rounded-lg border border-blue-500/30">
            <p className="text-xl text-gray-200 italic text-center leading-relaxed">
              "La medicina deja de ser reactiva para volverse proactiva, predictiva y humana."
            </p>
          </div>
          <div className="grid grid-cols-3 gap-4 mt-8">
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-400 mb-2">24/7</div>
              <div className="text-sm text-gray-400">Monitoreo continuo</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-purple-400 mb-2">∞</div>
              <div className="text-sm text-gray-400">Memoria de por vida</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-400 mb-2">1:1</div>
              <div className="text-sm text-gray-400">Cuidado personalizado</div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'closing',
      title: 'QuantIA',
      subtitle: 'Tu reflejo digital, tu guardián de vida, tu memoria médica eterna',
      content: (
        <div className="space-y-12">
          <div className="bg-gradient-to-br from-blue-900/40 via-purple-900/40 to-green-900/40 p-12 rounded-lg border-2 border-blue-500/30">
            <p className="text-3xl text-gray-100 font-light text-center leading-relaxed">
              QuantIA no es un asistente.
            </p>
            <p className="text-3xl text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-green-400 font-bold text-center leading-relaxed mt-4">
              Es tu reflejo digital, tu guardián de vida y tu memoria médica eterna.
            </p>
          </div>
          <div className="text-center space-y-4">
            <div className="text-xl text-gray-400">Desarrollado por</div>
            <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
              quantumq Lab
            </div>
            <div className="text-sm text-gray-500 mt-8">
              Construyendo el futuro del cuidado de salud inteligente y personalizado
            </div>
          </div>
        </div>
      )
    }
  ]

  const nextSlide = () => {
    if (currentSlide < slides.length - 1) {
      setDirection('next')
      setCurrentSlide(currentSlide + 1)
    }
  }

  const prevSlide = () => {
    if (currentSlide > 0) {
      setDirection('prev')
      setCurrentSlide(currentSlide - 1)
    }
  }

  const goToSlide = (index: number) => {
    setDirection(index > currentSlide ? 'next' : 'prev')
    setCurrentSlide(index)
  }

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault()
        nextSlide()
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault()
        prevSlide()
      } else if (e.key === 'Home') {
        e.preventDefault()
        goToSlide(0)
      } else if (e.key === 'End') {
        e.preventDefault()
        goToSlide(slides.length - 1)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [currentSlide])

  return (
    <>
      <Head>
        <title>Presentación QuantIA - quantumq Lab</title>
        <meta name="description" content="El Núcleo de la Vida Digital - Ecosistema Médico Inteligente" />
        <style>{`
          @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
          }
          @keyframes slideInUp {
            from {
              opacity: 0;
              transform: translateY(30px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          .animate-fadeIn {
            animation: fadeIn 0.5s ease-in-out;
          }
          .animate-slideInUp {
            animation: slideInUp 0.6s ease-out;
            animation-fill-mode: both;
          }
          .progress-bar {
            transition: width 0.3s ease-out;
          }
        `}</style>
      </Head>
      
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900/20 to-purple-900/20 text-white">
        {/* Progress bar */}
        <div className="fixed top-0 left-0 right-0 h-1 bg-gray-800 z-50">
          <div 
            className="progress-bar h-full bg-gradient-to-r from-blue-500 via-purple-500 to-green-500"
            style={{ width: `${((currentSlide + 1) / slides.length) * 100}%` }}
          />
        </div>

        {/* Navigation Bar */}
        <nav className="fixed top-1 left-0 right-0 bg-gray-900/80 backdrop-blur-sm border-b border-gray-700/50 z-50">
          <div className="container mx-auto px-6 py-4 flex items-center justify-between">
            <a href="/" className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 hover:scale-105 transition-transform">
              QuantIA
            </a>
            <div className="text-sm text-gray-400">
              Slide {currentSlide + 1} / {slides.length}
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <div className="pt-20 pb-24 px-6">
          <div className="container mx-auto max-w-6xl">
            {/* Slide Content with animation */}
            <div 
              key={currentSlide}
              className="min-h-[70vh] flex flex-col justify-center py-12 animate-fadeIn"
            >
              <div className="mb-8">
                <h1 className="text-5xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-green-400 animate-slideInUp">
                  {slides[currentSlide].title}
                </h1>
                <p className="text-xl text-gray-400 animate-slideInUp" style={{ animationDelay: '0.1s' }}>
                  {slides[currentSlide].subtitle}
                </p>
              </div>
              <div className="flex-1 animate-slideInUp" style={{ animationDelay: '0.2s' }}>
                {slides[currentSlide].content}
              </div>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="fixed bottom-0 left-0 right-0 bg-gray-900/80 backdrop-blur-sm border-t border-gray-700/50 z-50">
          <div className="container mx-auto px-4 sm:px-6 py-4 sm:py-6 max-w-6xl">
            {/* Dots Navigation */}
            <div className="flex items-center justify-center gap-2 mb-4 sm:mb-6 flex-wrap">
              {slides.map((slide, index) => (
                <button
                  key={index}
                  onClick={() => goToSlide(index)}
                  className={`h-2 rounded-full transition-all duration-300 ${
                    index === currentSlide
                      ? 'w-12 bg-gradient-to-r from-blue-500 to-purple-500 shadow-lg shadow-blue-500/50'
                      : index < currentSlide
                      ? 'w-2 bg-green-600 hover:bg-green-500'
                      : 'w-2 bg-gray-600 hover:bg-gray-500'
                  }`}
                  aria-label={`Ir al slide ${index + 1}: ${slide.title}`}
                  title={slide.title}
                />
              ))}
            </div>

            {/* Arrow Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-6">
              <button
                onClick={prevSlide}
                disabled={currentSlide === 0}
                className="w-full sm:w-auto px-8 py-3 bg-gray-800 hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed rounded-lg transition-all duration-300 font-semibold hover:scale-105 hover:shadow-lg text-sm sm:text-base"
              >
                ← Anterior
              </button>
              <a
                href="/"
                className="w-full sm:w-auto px-8 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-all duration-300 font-semibold hover:scale-105 hover:shadow-lg text-center text-sm sm:text-base"
              >
                Volver al Inicio
              </a>
              <button
                onClick={nextSlide}
                disabled={currentSlide === slides.length - 1}
                className="w-full sm:w-auto px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:opacity-30 disabled:cursor-not-allowed rounded-lg transition-all duration-300 font-semibold hover:scale-105 hover:shadow-lg hover:shadow-blue-500/50 text-sm sm:text-base"
              >
                Siguiente →
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}



